from collections.abc import Mapping
from functools import partial

from promise import Promise
from aiohttp import web
from graphql.type.schema import GraphQLSchema
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql_server import (
    HttpQueryError,
    default_format_error,
    encode_execution_results,
    json_encode,
    load_json_body,
    run_http_query,
)

from .render_graphiql import render_graphiql


class GraphQLView:  # pylint: disable = too-many-instance-attributes
    def __init__(
        self,
        schema=None,
        executor=None,
        root_value=None,
        context=None,
        pretty=False,
        graphiql=False,
        graphiql_version=None,
        graphiql_template=None,
        middleware=None,
        batch=False,
        jinja_env=None,
        max_age=86400,
        encoder=None,
        error_formatter=None,
        enable_async=True,
        subscriptions=None,
        **execution_options,
    ):
        # pylint: disable=too-many-arguments

        self.schema = schema
        self.executor = executor
        self.root_value = root_value
        self.context = context
        self.pretty = pretty
        self.graphiql = graphiql
        self.graphiql_version = graphiql_version
        self.graphiql_template = graphiql_template
        self.middleware = middleware
        self.batch = batch
        self.jinja_env = jinja_env
        self.max_age = max_age
        self.encoder = encoder or json_encode
        self.error_formatter = error_formatter or default_format_error
        self.enable_async = enable_async and isinstance(self.executor, AsyncioExecutor)
        self.subscriptions = subscriptions
        self.execution_options = execution_options
        assert isinstance(
            self.schema, GraphQLSchema
        ), "A Schema is required to be provided to GraphQLView."

    def get_context(self, request):
        if self.context and isinstance(self.context, Mapping):
            context = self.context.copy()
        else:
            context = {}

        if isinstance(context, Mapping) and "request" not in context:
            context.update({"request": request})
        return context

    async def parse_body(self, request):
        if request.content_type == "application/graphql":
            r_text = await request.text()
            return {"query": r_text}

        if request.content_type == "application/json":
            text = await request.text()
            return load_json_body(text)

        if request.content_type in (
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ):
            # TODO: seems like a multidict would be more appropriate
            # than casting it and de-duping variables. Alas, it's what
            # graphql-python wants.
            return dict(await request.post())

        return {}

    def render_graphiql(self, params, result):
        return render_graphiql(
            jinja_env=self.jinja_env,
            params=params,
            result=result,
            graphiql_version=self.graphiql_version,
            graphiql_template=self.graphiql_template,
            subscriptions=self.subscriptions,
        )

    def is_graphiql(self, request):
        return all(
            [
                self.graphiql,
                request.method.lower() == "get",
                "raw" not in request.query,
                any(
                    [
                        "text/html" in request.headers.get("accept", {}),
                        "*/*" in request.headers.get("accept", {}),
                    ]
                ),
            ]
        )

    def is_pretty(self, request):
        return any(
            [self.pretty, self.is_graphiql(request), request.query.get("pretty")]
        )

    async def __call__(self, request):
        try:
            data = await self.parse_body(request)
            request_method = request.method.lower()
            is_graphiql = self.is_graphiql(request)
            is_pretty = self.is_pretty(request)

            if request_method == "options":
                return self.process_preflight(request)

            execution_results, all_params = run_http_query(
                self.schema,
                request_method,
                data,
                query_data=request.query,
                batch_enabled=self.batch,
                catch=is_graphiql,
                # Execute options
                return_promise=self.enable_async,
                root_value=self.root_value,
                context_value=self.get_context(request),
                middleware=self.middleware,
                executor=self.executor,
                **self.execution_options,
            )

            if is_graphiql and self.enable_async:
                # catch errors like run_http_query does when async
                execution_results = [
                    result.catch(lambda value: None) for result in execution_results
                ]
            awaited_execution_results = await Promise.all(execution_results)
            result, status_code = encode_execution_results(
                awaited_execution_results,
                is_batch=isinstance(data, list),
                format_error=self.error_formatter,
                encode=partial(self.encoder, pretty=is_pretty),
            )

            if is_graphiql:
                return await self.render_graphiql(params=all_params[0], result=result,)

            return web.Response(
                text=result, status=status_code, content_type="application/json",
            )

        except HttpQueryError as err:
            return web.Response(
                text=self.encoder({"errors": [self.error_formatter(err)]}),
                status=err.status_code,
                headers=err.headers,
                content_type="application/json",
            )

    def process_preflight(self, request):
        """ Preflight request support for apollo-client
        https://www.w3.org/TR/cors/#resource-preflight-requests """
        headers = request.headers
        origin = headers.get("Origin", "")
        method = headers.get("Access-Control-Request-Method", "").upper()

        accepted_methods = ["GET", "POST", "PUT", "DELETE"]
        if method and method in accepted_methods:
            return web.Response(
                status=200,
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": ", ".join(accepted_methods),
                    "Access-Control-Max-Age": str(self.max_age),
                },
            )
        return web.Response(status=400)

    @classmethod
    def attach(cls, app, *, route_path="/graphql", route_name="graphql", **kwargs):
        view = cls(**kwargs)
        app.router.add_route("*", route_path, _asyncify(view), name=route_name)


def _asyncify(handler):
    """Return an async version of the given handler.

    This is mainly here because ``aiohttp`` can't infer the async definition of
    :py:meth:`.GraphQLView.__call__` and raises a :py:class:`DeprecationWarning`
    in tests. Wrapping it into an async function avoids the noisy warning.
    """

    async def _dispatch(request):
        return await handler(request)

    return _dispatch
