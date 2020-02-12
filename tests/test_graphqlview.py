import json

from urllib.parse import urlencode

import pytest

from aiohttp import FormData
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql.execution.executors.sync import SyncExecutor
from aiohttp_graphql import GraphQLView

from .schema import Schema, AsyncSchema


# pylint: disable=invalid-name
# pylint: disable=protected-access


@pytest.fixture
def view_kwargs():
    return {"schema": Schema}


@pytest.mark.parametrize(
    "view,expected",
    [
        (GraphQLView(schema=Schema), False),
        (GraphQLView(schema=Schema, executor=SyncExecutor()), False),
        (GraphQLView(schema=Schema, executor=AsyncioExecutor()), True),
    ],
)
def test_eval(view, expected):
    assert view.enable_async == expected


@pytest.mark.asyncio
async def test_allows_get_with_query_param(client, url_builder):
    response = await client.get(url_builder(query="{test}"))

    assert response.status == 200
    assert await response.json() == {"data": {"test": "Hello World"}}


@pytest.mark.asyncio
async def test_allows_get_with_variable_values(client, url_builder):
    response = await client.get(
        url_builder(
            query="query helloWho($who: String) { test(who: $who) }",
            variables=json.dumps({"who": "Dolly"}),
        )
    )

    assert response.status == 200
    assert await response.json() == {"data": {"test": "Hello Dolly"}}


@pytest.mark.asyncio
async def test_allows_get_with_operation_name(client, url_builder):
    response = await client.get(
        url_builder(
            query="""
        query helloYou { test(who: "You"), ...shared }
        query helloWorld { test(who: "World"), ...shared }
        query helloDolly { test(who: "Dolly"), ...shared }
        fragment shared on QueryRoot {
          shared: test(who: "Everyone")
        }
        """,
            operationName="helloWorld",
        )
    )

    assert response.status == 200
    assert await response.json() == {
        "data": {"test": "Hello World", "shared": "Hello Everyone"}
    }


@pytest.mark.asyncio
async def test_reports_validation_errors(client, url_builder):
    response = await client.get(url_builder(query="{ test, unknownOne, unknownTwo }"))

    assert response.status == 400
    assert await response.json() == {
        "errors": [
            {
                "message": 'Cannot query field "unknownOne" on type "QueryRoot".',
                "locations": [{"line": 1, "column": 9}],
            },
            {
                "message": 'Cannot query field "unknownTwo" on type "QueryRoot".',
                "locations": [{"line": 1, "column": 21}],
            },
        ],
    }


@pytest.mark.asyncio
async def test_errors_when_missing_operation_name(client, url_builder):
    response = await client.get(
        url_builder(
            query="""
        query TestQuery { test }
        mutation TestMutation { writeTest { test } }
        subscription TestSubscriptions { subscriptionsTest { test } }
        """
        )
    )

    assert response.status == 400
    assert await response.json() == {
        "errors": [
            {
                "message": (
                    "Must provide operation name if query contains multiple "
                    "operations."
                ),
            },
        ]
    }


@pytest.mark.asyncio
async def test_errors_when_sending_a_mutation_via_get(client, url_builder):
    response = await client.get(
        url_builder(
            query="""
        mutation TestMutation { writeTest { test } }
        """
        )
    )
    assert response.status == 405
    assert await response.json() == {
        "errors": [
            {"message": "Can only perform a mutation operation from a POST request."},
        ],
    }


@pytest.mark.asyncio
async def test_errors_when_selecting_a_mutation_within_a_get(client, url_builder):
    response = await client.get(
        url_builder(
            query="""
        query TestQuery { test }
        mutation TestMutation { writeTest { test } }
        """,
            operationName="TestMutation",
        )
    )

    assert response.status == 405
    assert await response.json() == {
        "errors": [
            {"message": "Can only perform a mutation operation from a POST request."},
        ],
    }


@pytest.mark.asyncio
async def test_errors_when_selecting_a_subscription_within_a_get(
    client, url_builder,
):
    response = await client.get(
        url_builder(
            query="""
        subscription TestSubscriptions { subscriptionsTest { test } }
        """,
            operationName="TestSubscriptions",
        )
    )

    assert response.status == 405
    assert await response.json() == {
        "errors": [
            {
                "message": (
                    "Can only perform a subscription operation from a POST " "request."
                )
            },
        ],
    }


@pytest.mark.asyncio
async def test_allows_mutation_to_exist_within_a_get(client, url_builder):
    response = await client.get(
        url_builder(
            query="""
        query TestQuery { test }
        mutation TestMutation { writeTest { test } }
        """,
            operationName="TestQuery",
        )
    )

    assert response.status == 200
    assert await response.json() == {"data": {"test": "Hello World"}}


@pytest.mark.asyncio
async def test_allows_post_with_json_encoding(client, base_url):
    response = await client.post(
        base_url,
        data=json.dumps(dict(query="{test}")),
        headers={"content-type": "application/json"},
    )

    assert await response.json() == {"data": {"test": "Hello World"}}
    assert response.status == 200


@pytest.mark.asyncio
async def test_allows_sending_a_mutation_via_post(client, base_url):
    response = await client.post(
        base_url,
        data=json.dumps(dict(query="mutation TestMutation { writeTest { test } }",)),
        headers={"content-type": "application/json"},
    )

    assert response.status == 200
    assert await response.json() == {"data": {"writeTest": {"test": "Hello World"}}}


@pytest.mark.asyncio
async def test_errors_when_sending_a_subscription_without_allow(client, base_url):
    response = await client.post(
        base_url,
        data=json.dumps(
            dict(
                query="""
            subscription TestSubscriptions { subscriptionsTest { test } }
            """,
            )
        ),
        headers={"content-type": "application/json"},
    )

    assert response.status == 200
    assert await response.json() == {
        "data": None,
        "errors": [
            {
                "message": "Subscriptions are not allowed. You will need to "
                "either use the subscribe function or pass "
                "allow_subscriptions=True"
            },
        ],
    }


@pytest.mark.asyncio
async def test_allows_post_with_url_encoding(client, base_url):
    data = FormData()
    data.add_field("query", "{test}")
    response = await client.post(
        base_url,
        data=data(),
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert await response.json() == {"data": {"test": "Hello World"}}
    assert response.status == 200


@pytest.mark.asyncio
async def test_supports_post_json_query_with_string_variables(client, base_url):
    response = await client.post(
        base_url,
        data=json.dumps(
            dict(
                query="query helloWho($who: String){ test(who: $who) }",
                variables=json.dumps({"who": "Dolly"}),
            )
        ),
        headers={"content-type": "application/json"},
    )

    assert response.status == 200
    assert await response.json() == {"data": {"test": "Hello Dolly"}}


@pytest.mark.asyncio
async def test_supports_post_json_query_with_json_variables(client, base_url):
    response = await client.post(
        base_url,
        data=json.dumps(
            dict(
                query="query helloWho($who: String){ test(who: $who) }",
                variables={"who": "Dolly"},
            )
        ),
        headers={"content-type": "application/json"},
    )

    assert response.status == 200
    assert await response.json() == {"data": {"test": "Hello Dolly"}}


@pytest.mark.asyncio
async def test_supports_post_url_encoded_query_with_string_variables(client, base_url):
    response = await client.post(
        base_url,
        data=urlencode(
            dict(
                query="query helloWho($who: String){ test(who: $who) }",
                variables=json.dumps({"who": "Dolly"}),
            ),
        ),
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response.status == 200
    assert await response.json() == {"data": {"test": "Hello Dolly"}}


@pytest.mark.asyncio
async def test_supports_post_json_quey_with_get_variable_values(client, url_builder):
    response = await client.post(
        url_builder(variables=json.dumps({"who": "Dolly"})),
        data=json.dumps(dict(query="query helloWho($who: String){ test(who: $who) }",)),
        headers={"content-type": "application/json"},
    )

    assert response.status == 200
    assert await response.json() == {"data": {"test": "Hello Dolly"}}


@pytest.mark.asyncio
async def test_post_url_encoded_query_with_get_variable_values(client, url_builder):
    response = await client.post(
        url_builder(variables=json.dumps({"who": "Dolly"})),
        data=urlencode(dict(query="query helloWho($who: String){ test(who: $who) }",)),
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response.status == 200
    assert await response.json() == {"data": {"test": "Hello Dolly"}}


@pytest.mark.asyncio
async def test_supports_post_raw_text_query_with_get_variable_values(
    client, url_builder
):
    response = await client.post(
        url_builder(variables=json.dumps({"who": "Dolly"})),
        data="query helloWho($who: String){ test(who: $who) }",
        headers={"content-type": "application/graphql"},
    )

    assert response.status == 200
    assert await response.json() == {"data": {"test": "Hello Dolly"}}


@pytest.mark.asyncio
async def test_allows_post_with_operation_name(client, base_url):
    response = await client.post(
        base_url,
        data=json.dumps(
            dict(
                query="""
            query helloYou { test(who: "You"), ...shared }
            query helloWorld { test(who: "World"), ...shared }
            query helloDolly { test(who: "Dolly"), ...shared }
            fragment shared on QueryRoot {
              shared: test(who: "Everyone")
            }
            """,
                operationName="helloWorld",
            )
        ),
        headers={"content-type": "application/json"},
    )

    assert response.status == 200
    assert await response.json() == {
        "data": {"test": "Hello World", "shared": "Hello Everyone"}
    }


@pytest.mark.asyncio
async def test_allows_post_with_get_operation_name(client, url_builder):
    response = await client.post(
        url_builder(operationName="helloWorld"),
        data="""
        query helloYou { test(who: "You"), ...shared }
        query helloWorld { test(who: "World"), ...shared }
        query helloDolly { test(who: "Dolly"), ...shared }
        fragment shared on QueryRoot {
          shared: test(who: "Everyone")
        }
        """,
        headers={"content-type": "application/graphql"},
    )

    assert response.status == 200
    assert await response.json() == {
        "data": {"test": "Hello World", "shared": "Hello Everyone"}
    }


@pytest.mark.asyncio
async def test_supports_pretty_printing(client, url_builder):
    response = await client.get(url_builder(query="{test}", pretty="1"))

    text = await response.text()
    assert text == ("{\n" '  "data": {\n' '    "test": "Hello World"\n' "  }\n" "}")


@pytest.mark.asyncio
async def test_not_pretty_by_default(client, url_builder):
    response = await client.get(url_builder(query="{test}"))

    assert await response.text() == ('{"data":{"test":"Hello World"}}')


@pytest.mark.asyncio
async def test_supports_pretty_printing_by_request(client, url_builder):
    response = await client.get(url_builder(query="{test}", pretty="1"))

    assert await response.text() == (
        "{\n" '  "data": {\n' '    "test": "Hello World"\n' "  }\n" "}"
    )


@pytest.mark.asyncio
async def test_handles_field_errors_caught_by_graphql(client, url_builder):
    response = await client.get(url_builder(query="{thrower}"))
    assert response.status == 200
    assert await response.json() == {
        "data": None,
        "errors": [
            {
                "locations": [{"column": 2, "line": 1}],
                "message": "Throws!",
                "path": ["thrower"],
            }
        ],
    }


@pytest.mark.asyncio
async def test_handles_syntax_errors_caught_by_graphql(client, url_builder):
    response = await client.get(url_builder(query="syntaxerror"))

    assert response.status == 400
    assert await response.json() == {
        "errors": [
            {
                "locations": [{"column": 1, "line": 1}],
                "message": (
                    "Syntax Error GraphQL (1:1) "
                    'Unexpected Name "syntaxerror"\n\n1: syntaxerror\n   ^\n'
                ),
            },
        ],
    }


@pytest.mark.asyncio
async def test_handles_errors_caused_by_a_lack_of_query(client, base_url):
    response = await client.get(base_url)

    assert response.status == 400
    assert await response.json() == {
        "errors": [{"message": "Must provide query string."}]
    }


@pytest.mark.asyncio
async def test_handles_batch_correctly_if_is_disabled(client, base_url):
    response = await client.post(
        base_url, data="[]", headers={"content-type": "application/json"},
    )

    assert response.status == 400
    assert await response.json() == {
        "errors": [{"message": "Batch GraphQL requests are not enabled."}]
    }


@pytest.mark.asyncio
async def test_handles_incomplete_json_bodies(client, base_url):
    response = await client.post(
        base_url, data='{"query":', headers={"content-type": "application/json"},
    )

    assert response.status == 400
    assert await response.json() == {
        "errors": [{"message": "POST body sent invalid JSON."}]
    }


@pytest.mark.asyncio
async def test_handles_plain_post_text(client, url_builder):
    response = await client.post(
        url_builder(variables=json.dumps({"who": "Dolly"})),
        data="query helloWho($who: String){ test(who: $who) }",
        headers={"content-type": "text/plain"},
    )
    assert response.status == 400
    assert await response.json() == {
        "errors": [{"message": "Must provide query string."}]
    }


@pytest.mark.asyncio
async def test_handles_poorly_formed_variables(client, url_builder):
    response = await client.get(
        url_builder(
            query="query helloWho($who: String){ test(who: $who) }", variables="who:You"
        ),
    )
    assert response.status == 400
    assert await response.json() == {
        "errors": [{"message": "Variables are invalid JSON."}]
    }


@pytest.mark.asyncio
async def test_handles_unsupported_http_methods(client, url_builder):
    response = await client.put(url_builder(query="{test}"))
    assert response.status == 405
    assert response.headers["Allow"] in ["GET, POST", "HEAD, GET, POST, OPTIONS"]
    assert await response.json() == {
        "errors": [{"message": "GraphQL only supports GET and POST requests."}]
    }


@pytest.mark.asyncio
async def test_passes_request_into_request_context(client, url_builder):
    response = await client.get(url_builder(query="{request}", q="testing"))

    assert response.status == 200
    assert await response.json() == {
        "data": {"request": "testing"},
    }


class TestCustomContext:
    @pytest.fixture
    def view_kwargs(self, request, view_kwargs):
        # pylint: disable=no-self-use
        # pylint: disable=redefined-outer-name
        view_kwargs.update(context=request.param)
        return view_kwargs

    @pytest.mark.parametrize(
        "view_kwargs",
        ["CUSTOM CONTEXT", {"CUSTOM_CONTEXT": "test"}],
        indirect=True,
        ids=repr,
    )
    @pytest.mark.asyncio
    async def test_context_remapped(self, client, url_builder):
        response = await client.get(url_builder(query="{context}"))

        _json = await response.json()
        assert response.status == 200
        assert "request" in _json["data"]["context"]
        assert "CUSTOM CONTEXT" not in _json["data"]["context"]

    @pytest.mark.parametrize(
        "view_kwargs", [{"request": "test"}], indirect=True, ids=repr
    )
    @pytest.mark.asyncio
    async def test_request_not_replaced(self, client, url_builder):
        response = await client.get(url_builder(query="{context}"))

        _json = await response.json()
        assert response.status == 200
        assert "request" in _json["data"]["context"]
        assert _json["data"]["context"] == str({"request": "test"})


@pytest.mark.asyncio
async def test_post_multipart_data(client, base_url):
    # pylint: disable=line-too-long
    query = "mutation TestMutation { writeTest { test } }"

    data = (
        "------aiohttpgraphql\r\n"
        + 'Content-Disposition: form-data; name="query"\r\n'
        + "\r\n"
        + query
        + "\r\n"
        + "------aiohttpgraphql--\r\n"
        + "Content-Type: text/plain; charset=utf-8\r\n"
        + 'Content-Disposition: form-data; name="file"; filename="text1.txt"; filename*=utf-8\'\'text1.txt\r\n'
        + "\r\n"
        + "\r\n"
        + "------aiohttpgraphql--\r\n"
    )

    response = await client.post(
        base_url,
        data=data,
        headers={"content-type": "multipart/form-data; boundary=----aiohttpgraphql"},
    )

    assert response.status == 200
    assert await response.json() == {"data": {u"writeTest": {u"test": u"Hello World"}}}


class TestBatchExecutor:
    @pytest.fixture
    def view_kwargs(self, view_kwargs):
        # pylint: disable=no-self-use
        # pylint: disable=redefined-outer-name
        view_kwargs.update(batch=True)
        return view_kwargs

    @pytest.mark.asyncio
    async def test_batch_allows_post_with_json_encoding(self, client, base_url):
        response = await client.post(
            base_url,
            data=json.dumps([dict(id=1, query="{test}")]),
            headers={"content-type": "application/json"},
        )

        assert response.status == 200
        assert await response.json() == [{"data": {"test": "Hello World"}}]

    @pytest.mark.asyncio
    async def test_batch_supports_post_json_query_with_json_variables(
        self, client, base_url
    ):
        response = await client.post(
            base_url,
            data=json.dumps(
                [
                    dict(
                        id=1,
                        query="query helloWho($who: String){ test(who: $who) }",
                        variables={"who": "Dolly"},
                    )
                ]
            ),
            headers={"content-type": "application/json"},
        )

        assert response.status == 200
        assert await response.json() == [{"data": {"test": "Hello Dolly"}}]

    @pytest.mark.asyncio
    async def test_batch_allows_post_with_operation_name(self, client, base_url):
        response = await client.post(
            base_url,
            data=json.dumps(
                [
                    dict(
                        id=1,
                        query="""
                query helloYou { test(who: "You"), ...shared }
                query helloWorld { test(who: "World"), ...shared }
                query helloDolly { test(who: "Dolly"), ...shared }
                fragment shared on QueryRoot {
                  shared: test(who: "Everyone")
                }
                """,
                        operationName="helloWorld",
                    )
                ]
            ),
            headers={"content-type": "application/json"},
        )

        assert response.status == 200
        assert await response.json() == [
            {"data": {"test": "Hello World", "shared": "Hello Everyone"}}
        ]


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
    async def test_async_schema(self, client, url_builder):
        response = await client.get(url_builder(query="{a,b,c}"))

        assert response.status == 200
        assert await response.json() == {"data": {"a": "hey", "b": "hey2", "c": "hey3"}}


@pytest.mark.asyncio
async def test_preflight_request(client, base_url):
    response = await client.options(
        base_url, headers={"Access-Control-Request-Method": "POST"},
    )

    assert response.status == 200


@pytest.mark.asyncio
async def test_preflight_incorrect_request(client, base_url):
    response = await client.options(
        base_url, headers={"Access-Control-Request-Method": "OPTIONS"},
    )

    assert response.status == 400
