from urllib.parse import urlencode

import pytest

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from graphql.execution.executors.asyncio import AsyncioExecutor

from aiohttp_graphql import GraphQLView

# pylint: disable=redefined-outer-name


# GraphQL Fixtures
@pytest.fixture(params=[True, False], ids=["async", "sync"])
def executor(request):
    if request.param:
        return AsyncioExecutor()
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
async def client(app):
    client = TestClient(TestServer(app))
    await client.start_server()
    yield client
    await client.close()


# URL Fixtures
@pytest.fixture
def base_url():
    return "/graphql"


@pytest.fixture
def url_builder(base_url):
    def builder(**url_params):
        if url_params:
            return "{}?{}".format(base_url, urlencode(url_params))
        return base_url

    return builder
