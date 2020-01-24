import asyncio

from graphql.type.definition import (
    GraphQLArgument,
    GraphQLField,
    GraphQLNonNull,
    GraphQLObjectType,
)
from graphql.type.scalars import GraphQLString
from graphql.type.schema import GraphQLSchema


def resolve_raises(*args):
    # pylint: disable=unused-argument
    raise Exception("Throws!")


# Sync schema
QueryRootType = GraphQLObjectType(
    name="QueryRoot",
    fields={
        "thrower": GraphQLField(
            GraphQLNonNull(GraphQLString), resolver=resolve_raises,
        ),
        "request": GraphQLField(
            GraphQLNonNull(GraphQLString),
            resolver=lambda obj, info, *args: info.context["request"].query.get("q"),
        ),
        "context": GraphQLField(
            GraphQLNonNull(GraphQLString),
            resolver=lambda obj, info, *args: info.context,
        ),
        "test": GraphQLField(
            type=GraphQLString,
            args={"who": GraphQLArgument(GraphQLString)},
            resolver=lambda obj, info, **args: "Hello %s"
            % (args.get("who") or "World"),
        ),
    },
)


MutationRootType = GraphQLObjectType(
    name="MutationRoot",
    fields={
        "writeTest": GraphQLField(
            type=QueryRootType, resolver=lambda *args: QueryRootType
        )
    },
)

SubscriptionsRootType = GraphQLObjectType(
    name="SubscriptionsRoot",
    fields={
        "subscriptionsTest": GraphQLField(
            type=QueryRootType, resolver=lambda *args: QueryRootType
        )
    },
)

Schema = GraphQLSchema(QueryRootType, MutationRootType, SubscriptionsRootType)


# Schema with async methods
async def resolver(context, *args):
    # pylint: disable=unused-argument
    await asyncio.sleep(0.001)
    return "hey"


async def resolver_2(context, *args):
    # pylint: disable=unused-argument
    await asyncio.sleep(0.003)
    return "hey2"


def resolver_3(context, *args):
    # pylint: disable=unused-argument
    return "hey3"


AsyncQueryType = GraphQLObjectType(
    "AsyncQueryType",
    {
        "a": GraphQLField(GraphQLString, resolver=resolver),
        "b": GraphQLField(GraphQLString, resolver=resolver_2),
        "c": GraphQLField(GraphQLString, resolver=resolver_3),
    },
)


AsyncSchema = GraphQLSchema(AsyncQueryType)
