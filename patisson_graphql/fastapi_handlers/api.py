from contextlib import _AsyncGeneratorContextManager

from ariadne import graphql
from fastapi import Request
from graphql import GraphQLSchema
from sqlalchemy.ext.asyncio import AsyncSession


async def graphql_server(request: Request, schema: GraphQLSchema,
                         session_gen: _AsyncGeneratorContextManager[AsyncSession]):
    data = await request.json()
    async with session_gen as session:
        success, result = await graphql(
            schema,
            data,
            context_value={"db": session}, 
            debug=True,
        )
    return result

