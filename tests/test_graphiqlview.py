from graphql.execution.executors.asyncio import AsyncioExecutor

from jinja2 import Environment

import pytest

from .schema import (
    AsyncSchema,
    Schema,
)

# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name


@pytest.fixture
def pretty_response():
    return (
        ("{\n" '  "data": {\n' '    "test": "Hello World"\n' "  }\n" "}")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


@pytest.fixture
def view_kwargs():
    return {
        "schema": Schema,
        "graphiql": True,
    }


@pytest.mark.asyncio
async def test_graphiql_is_enabled(client, base_url):
    response = await client.get(base_url, headers={"Accept": "text/html"})
    assert response.status == 200


@pytest.mark.asyncio
async def test_graphiql_simple_renderer(client, url_builder, pretty_response):
    response = await client.get(
        url_builder(query="{test}"), headers={"Accept": "text/html"},
    )
    assert response.status == 200
    assert pretty_response in await response.text()


class TestJinjaEnv:
    @pytest.fixture(params=[True, False], ids=["async_jinja2", "sync_jinja2"])
    def view_kwargs(self, request, view_kwargs):
        # pylint: disable=no-self-use
        # pylint: disable=redefined-outer-name
        view_kwargs.update(jinja_env=Environment(enable_async=request.param))
        return view_kwargs

    @pytest.mark.asyncio
    async def test_graphiql_jinja_renderer(self, client, url_builder, pretty_response):
        response = await client.get(
            url_builder(query="{test}"), headers={"Accept": "text/html"},
        )
        assert response.status == 200
        assert pretty_response in await response.text()


@pytest.mark.asyncio
async def test_graphiql_html_is_not_accepted(client, base_url):
    response = await client.get(base_url, headers={"Accept": "application/json"},)
    assert response.status == 400


@pytest.mark.asyncio
async def test_graphiql_get_mutation(client, url_builder):
    response = await client.get(
        url_builder(query="mutation TestMutation { writeTest { test } }"),
        headers={"Accept": "text/html"},
    )
    assert response.status == 200
    assert "response: null" in await response.text()


@pytest.mark.asyncio
async def test_graphiql_get_subscriptions(client, url_builder):
    response = await client.get(
        url_builder(
            query=("subscription TestSubscriptions { subscriptionsTest { test } }")
        ),
        headers={"Accept": "text/html"},
    )
    assert response.status == 200
    assert "response: null" in await response.text()


class TestAsyncSchema:
    @pytest.fixture
    def executor(self, event_loop):
        # pylint: disable=no-self-use
        # Only need to test with the AsyncExecutor
        return AsyncioExecutor(loop=event_loop)

    @pytest.fixture
    def view_kwargs(self, view_kwargs):
        # pylint: disable=no-self-use
        # pylint: disable=redefined-outer-name
        view_kwargs.update(schema=AsyncSchema)
        return view_kwargs

    @pytest.mark.asyncio
    async def test_graphiql_asyncio_schema(self, client, url_builder):
        response = await client.get(
            url_builder(query="{a,b,c}"), headers={"Accept": "text/html"},
        )

        expected_response = (
            (
                "{\n"
                '  "data": {\n'
                '    "a": "hey",\n'
                '    "b": "hey2",\n'
                '    "c": "hey3"\n'
                "  }\n"
                "}"
            )
            .replace('"', '\\"')
            .replace("\n", "\\n")
        )

        assert response.status == 200
        assert expected_response in await response.text()
