# aiohttp-graphql

Adds [GraphQL] support to your [aiohttp] application.

Based on [flask-graphql] by [Syrus Akbary] and [sanic-graphql] by [Sergey Porivaev].

[![travis][travis-image]][travis-url]
[![pyversion][pyversion-image]][pyversion-url]
[![pypi][pypi-image]][pypi-url]
[![Anaconda-Server Badge][conda-image]][conda-url]
[![codecov][codecov-image]][codecov-url]

[travis-image]: https://travis-ci.com/graphql-python/aiohttp-graphql.svg?style=flat
[travis-url]: https://travis-ci.com/graphql-python/aiohttp-graphql/
[pyversion-image]: https://img.shields.io/pypi/pyversions/aiohttp-graphql
[pyversion-url]: https://pypi.org/project/aiohttp-graphql/
[pypi-image]: https://img.shields.io/pypi/v/aiohttp-graphql.svg?style=flat
[pypi-url]: https://pypi.org/project/aiohttp-graphql/
[codecov-image]: https://codecov.io/gh/graphql-python/aiohttp-graphql/branch/master/graph/badge.svg
[codecov-url]: https://codecov.io/gh/graphql-python/aiohttp-graphql/
[conda-image]: https://img.shields.io/conda/vn/conda-forge/aiohttp-graphql.svg
[conda-url]: https://anaconda.org/conda-forge/aiohttp-graphql


## Usage

Use the `GraphQLView` view from `aiohttp_graphql`

```python
from aiohttp import web
from aiohttp_graphql import GraphQLView

from schema import schema

app = web.Application()

GraphQLView.attach(app, schema=schema, graphiql=True)

# Optional, for adding batch query support (used in Apollo-Client)
GraphQLView.attach(app, schema=schema, batch=True, route_path="/graphql/batch")

if __name__ == '__main__':
    web.run_app(app)
```

This will add `/graphql` endpoint to your app (customizable by passing `route_path='/mypath'` to `GraphQLView.attach`) and enable the GraphiQL IDE.

Note: `GraphQLView.attach` is just a convenience function, and the same functionality can be achieved with

```python
gql_view = GraphQLView(schema=schema, graphiql=True)
app.router.add_route('*', '/graphql', gql_view, name='graphql')
```

It's worth noting that the the "view function" of `GraphQLView` is contained in `GraphQLView.__call__`. So, when you create an instance, that instance is callable with the request object as the sole positional argument. To illustrate:

```python
gql_view = GraphQLView(schema=Schema, **kwargs)
gql_view(request)  # <-- the instance is callable and expects a `aiohttp.web.Request` object.
```

### Supported options for GraphQLView

 * `schema`: The `GraphQLSchema` object that you want the view to execute when it gets a valid request.
 * `context`: A value to pass as the `context_value` to graphql `execute` function. By default is set to `dict` with request object at key `request`.
 * `root_value`: The `root_value` you want to provide to graphql `execute`.
 * `pretty`: Whether or not you want the response to be pretty printed JSON.
 * `graphiql`: If `True`, may present [GraphiQL](https://github.com/graphql/graphiql) when loaded directly from a browser (a useful tool for debugging and exploration).
 * `graphiql_version`: The graphiql version to load. Defaults to **"1.0.3"**.
 * `graphiql_template`: Inject a Jinja template string to customize GraphiQL.
 * `graphiql_html_title`: The graphiql title to display. Defaults to **"GraphiQL"**.
 * `jinja_env`: Sets jinja environment to be used to process GraphiQL template. If Jinja’s async mode is enabled (by `enable_async=True`), uses 
`Template.render_async` instead of `Template.render`. If environment is not set, fallbacks to simple regex-based renderer.
 * `batch`: Set the GraphQL view as batch (for using in [Apollo-Client](http://dev.apollodata.com/core/network.html#query-batching) or [ReactRelayNetworkLayer](https://github.com/nodkz/react-relay-network-layer))
 * `middleware`: A list of graphql [middlewares](http://docs.graphene-python.org/en/latest/execution/middleware/).
 * `max_age`: Sets the response header Access-Control-Max-Age for preflight requests.
 * `encode`: the encoder to use for responses (sensibly defaults to `graphql_server.json_encode`).
 * `format_error`: the error formatter to use for responses (sensibly defaults to `graphql_server.default_format_error`.
 * `enable_async`: whether `async` mode will be enabled.
 * `subscriptions`: The GraphiQL socket endpoint for using subscriptions in graphql-ws.
 * `headers`: An optional GraphQL string to use as the initial displayed request headers, if not provided, the stored headers will be used.
 * `default_query`: An optional GraphQL string to use when no query is provided and no stored query exists from a previous session. If not provided, GraphiQL will use its own default query.
* `header_editor_enabled`: An optional boolean which enables the header editor when true. Defaults to **false**.
* `should_persist_headers`:  An optional boolean which enables to persist headers to storage when true. Defaults to **false**.


## Contributing
Since v3, `aiohttp-graphql` code lives at [graphql-server](https://github.com/graphql-python/graphql-server) repository to keep any breaking change on the base package on sync with all other integrations. In order to contribute, please take a look at [CONTRIBUTING.md](https://github.com/graphql-python/graphql-server/blob/master/CONTRIBUTING.md).


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
