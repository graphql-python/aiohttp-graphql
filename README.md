aiohttp-graphql
===============

Adds [GraphQL] support to your [aiohttp] application.

Based on [flask-graphql] by [Syrus Akbary].

Usage
-----

Just use the `GraphQLView` view from `aiohttp_graphql`

```python
from aiohttp_graphql import GraphQLView

GraphQLView.attach(app, schema=Schema, graphiql=True)

# Optional, for adding batch query support (used in Apollo-Client)
GraphQLView.attach(app, schema=Schema, batch=True)
```

This will add a `/graphql` endpoint to your app (customizable by passing `route_path='/mypath'` to `GraphQLView.attach`)

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


License
-------

Copyright for portions of project [aiohttp-graphql] are held by [Syrus Akbary] as part of project [flask-graphql]. All other claims to this project [aiohttp-graphql] are held by [Devin Fee].

This project is licensed under MIT License.

  [GraphQL]: http://graphql.org/
  [aiohttp]: https://github.com/aio-libs/aiohttp/
  [flask-graphql]: https://github.com/graphql-python/flask-graphql
  [Syrus Akbary]: https://github.com/syrusakbary
  [GraphiQL]: https://github.com/graphql/graphiql
  [graphql-python]: https://github.com/graphql-python/graphql-core
  [Apollo-Client]: http://dev.apollodata.com/core/network.html#query-batching
  [Devin Fee]: https://github.com/dfee
  [aiohttp-graphql]: https://github.com/dfee/aiohttp-graphql
