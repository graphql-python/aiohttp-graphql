from urllib.parse import urlencode

from aiohttp import web
import aiohttp.test_utils
from graphql.execution.executors.asyncio import AsyncioExecutor
import pytest

from aiohttp_graphql import GraphQLView

# pylint: disable=redefined-outer-name


# GraphQL Fixtures
@pytest.fixture(params=[True, False], ids=['async', 'sync'])
def executor(request, event_loop):
    if request.param:
        return AsyncioExecutor(event_loop)
    return None


# GraphQLView Fixtures
@pytest.fixture
def view_kwargs():
    return {}


# aiohttp Fixtures
@pytest.fixture
def app(executor, view_kwargs):
    app = web.Application()
    GraphQLView.attach(app, executor=executor, **view_kwargs)
    return app


@pytest.fixture
async def client(event_loop, app):
    client = aiohttp.test_utils.TestClient(aiohttp.test_utils.TestServer(app), loop=event_loop)
    await client.start_server()
    yield client
    await client.close()



# URL Fixtures
@pytest.fixture
def base_url():
    return '/graphql'


@pytest.fixture
def url_builder(base_url):
    def builder(**url_params):
        if url_params:
            return '{}?{}'.format(base_url, urlencode(url_params))
        return base_url
    return builder
