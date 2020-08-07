from urllib.parse import urlencode

from aiohttp import web

from aiohttp_graphql import GraphQLView
from tests.schema import Schema


def create_app(schema=Schema, **kwargs):
    app = web.Application()
    # Only needed to silence aiohttp deprecation warnings
    GraphQLView.attach(app, schema=schema, **kwargs)
    return app


def url_string(**url_params):
    base_url = "/graphql"

    if url_params:
        return f"{base_url}?{urlencode(url_params)}"

    return base_url
