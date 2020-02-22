# aiohttp-graphql
Adds [GraphQL] support to your [aiohttp] application.

Based on [flask-graphql] by [Syrus Akbary] and [sanic-graphql] by [Sergey Porivaev].

[![PyPI version](https://badge.fury.io/py/aiohttp-graphql.svg)](https://badge.fury.io/py/aiohttp-graphql)
[![Build Status](https://travis-ci.com/graphql-python/aiohttp-graphql.svg?branch=master)](https://github.com/graphql-python/aiohttp-graphql)
[![Coverage Status](https://codecov.io/gh/graphql-python/aiohttp-graphql/branch/master/graph/badge.svg)](https://github.com/graphql-python/aiohttp-graphql)

## Usage
Just use the `GraphQLView` view from `aiohttp_graphql`

```python
from aiohttp_graphql import GraphQLView

GraphQLView.attach(app, schema=Schema, graphiql=True)

# Optional, for adding batch query support (used in Apollo-Client)
GraphQLView.attach(app, schema=Schema, batch=True)
```

This will add a `/graphql` endpoint to your app (customizable by passing `route_path='/mypath'` to `GraphQLView.attach`).

Note: `GraphQLView.attach` is just a convenience function, and the same functionality can be achieved with

```python
gql_view = GraphQLView(schema=Schema, **kwargs)
app.router.add_route('*', gql_view, name='graphql')
```

It's worth noting that the the "view function" of `GraphQLView` is contained in `GraphQLView.__call__`. So, when you create an instance, that instance is callable with the request object as the sole positional argument. To illustrate:

```python
gql_view = GraphQLView(schema=Schema, **kwargs)
gql_view(request)  # <-- the instance is callable and expects a `aiohttp.web.Request` object.
```

### Supported options
-   `schema`: The `GraphQLSchema` object that you want the view to execute when it gets a valid request.
-   `executor`: The `Executor` that you want to use to execute queries. If an `AsyncioExecutor` instance is provided, performs queries asynchronously within executor’s loop.
-   `root_value`: The `root_value` you want to provide to `executor.execute`.
-   `context`: A value to pass as the `context` to the `graphql()` function. By default is set to `dict` with request object at key `request`.
-   `pretty`: Whether or not you want the response to be pretty printed JSON.
-   `graphiql`: If `True`, may present [GraphiQL] when loaded directly from a browser (a useful tool for debugging and exploration).
-   `graphiql_version`: The version of the provided `graphiql` package.
-   `graphiql_template`: Inject a Jinja template string to customize GraphiQL.
-   `middleware`: Custom middleware for [graphql-python].
-   `batch`: Set the GraphQL view as batch (for using in [Apollo-Client] or [ReactRelayNetworkLayer])
-   `jinja_env`: Sets jinja environment to be used to process GraphiQL template. If Jinja’s async mode is enabled (by `enable_async=True`), uses
`Template.render_async` instead of `Template.render`. If environment is not set, fallbacks to simple regex-based renderer.
-   `max_age`: sets the response header `Access-Control-Max-Age` for preflight requests
-   `encoder`: the encoder to use for responses (sensibly defaults to `graphql_server.json_encode`)
-   `error_formatter`: the error formatter to use for responses (sensibly defaults to `graphql_server.default_format_error`)
-   `enable_async`: whether `async` mode will be enabled.
-   `subscriptions`: The [GraphiQL] socket endpoint for using subscriptions in [graphql-ws].


## Testing
Testing is done with `pytest`.

```bash
git clone https://github.com/graphql-python/aiohttp-graphql
cd aiohttp-graphql
# Create a virtualenv
python3.6 -m venv env && source env/bin/activate  # for example
pip install -e .[test]
pytest
```

The tests, while modeled after sanic-graphql's tests, have been entirely refactored to take advantage of `pytest-asyncio`, conform with PEP-8, and increase readability with pytest fixtures. For usage tests, please check them out.


## License
Copyright for portions of project [aiohttp-graphql] are held by [Syrus Akbary] as part of project [flask-graphql] and [sanic-graphql] as part of project [Sergey Porivaev]. All other claims to this project [aiohttp-graphql] are held by [Devin Fee].

This project is licensed under the MIT License.

  [GraphQL]: http://graphql.org/
  [aiohttp]: https://github.com/aio-libs/aiohttp/
  [flask-graphql]: https://github.com/graphql-python/flask-graphql
  [sanic-graphql]: https://github.com/graphql-python/sanic-graphql
  [Syrus Akbary]: https://github.com/syrusakbary
  [Sergey Porivaev]: https://github.com/grazor
  [GraphiQL]: https://github.com/graphql/graphiql
  [graphql-python]: https://github.com/graphql-python/graphql-core
  [Apollo-Client]: https://www.apollographql.com/docs/react/networking/network-layer/#query-batching
  [Devin Fee]: https://github.com/dfee
  [aiohttp-graphql]: https://github.com/graphql-python/aiohttp-graphql
  [graphql-ws]: https://github.com/graphql-python/graphql-ws
