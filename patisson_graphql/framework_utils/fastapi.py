"""
This module provides utilities for integrating GraphQL functionality into a FastAPI application.

Using the Ariadne library. It includes tools for schema creation, GraphQL request processing,
and seamless database session management.

Utilities:

1. GraphQLContext:
   - A base class for the GraphQL context, providing access to the request, database session,
     and optional user/service payloads.
   - Extendable for additional context fields with default values.

2. graphql_server:
   - The core function to handle GraphQL requests.
   - Executes queries against a provided schema and manages the lifecycle of the database session.

3. create_graphql_route:
   - A utility to create FastAPI-compatible routes for GraphQL endpoints.
   - Supports schema loading, resolver injection, and dynamic session management.

Features:
- Seamless integration with Ariadne's schema execution.
- Customizable GraphQL context with support for additional fields.
- Simple and reusable utilities for defining and managing GraphQL routes in FastAPI.
- Works with asynchronous database sessions for efficient request handling.
"""

from contextlib import _AsyncGeneratorContextManager
from typing import Awaitable, Callable, Generic, Optional, TypeVar

from ariadne import graphql, load_schema_from_path, make_executable_schema
from fastapi import Request
from graphql import GraphQLSchema
from patisson_request.jwt_tokens import ClientAccessTokenPayload, ServiceAccessTokenPayload
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

ServicePayloadTypeVar = TypeVar("ServicePayloadTypeVar", bound=Optional[ServiceAccessTokenPayload])
UserPayloadTypeVar = TypeVar("UserPayloadTypeVar", bound=Optional[ClientAccessTokenPayload])
SessionGenType = Callable[..., _AsyncGeneratorContextManager[AsyncSession]]


class GraphQLContext(BaseModel, Generic[ServicePayloadTypeVar, UserPayloadTypeVar]):
    """
    This class defines the base context for GraphQL resolvers in the application.

    It includes the essential attributes required during the execution of a GraphQL operation.

    Attributes:
        request (Request): The HTTP request object, which provides access to the headers,
                           method, URL, and body of the incoming GraphQL request.
        db_session (AsyncSession): The asynchronous database session for performing database operations.
        service (ServicePayloadTypeVar, optional): The service payload, typically used to store
                                                   data related to the current service. Defaults to None.
        user (UserPayloadTypeVar, optional): The user payload, typically used to store information
                                             about the current user. Defaults to None.

    Configuration:
        - `arbitrary_types_allowed` is set to `True` to allow non-Pydantic types, such as `Request`.

    Extending the Context:
        If additional fields are needed in the GraphQL context (e.g., a caching mechanism,
        additional metadata, etc.), you should inherit from this base class.
        Any new fields added must:
        - Have a default value, such as `None`.
        - Be configurable either in a decorator wrapping the resolver or directly within the resolver.
    """

    request: Request
    db_session: AsyncSession
    service: ServicePayloadTypeVar = None  # type: ignore[reportAssignmentType]
    user: UserPayloadTypeVar = None  # type: ignore[reportAssignmentType]

    class Config:
        arbitrary_types_allowed = True


async def graphql_server(
    request: Request,
    schema: GraphQLSchema,
    session_gen: _AsyncGeneratorContextManager,
    context: type[GraphQLContext] = GraphQLContext,
    **kwargs
):
    """
    Serve as the main entry point for processing GraphQL requests.

    Args:
        request (Request): The incoming HTTP request containing the GraphQL query and variables.
        schema (GraphQLSchema): The executable GraphQL schema to resolve the queries against.
        session_gen (_AsyncGeneratorContextManager): A callable or generator function that provides
                                                     an asynchronous database session.
        context (type[GraphQLContext], optional): A class or subclass of `GraphQLContext` used to
                                                  generate the context for GraphQL resolvers.
                                                  Defaults to `GraphQLContext`.
        **kwargs: Additional arguments to be passed to the GraphQL execution engine.

    Workflow:
        1. Opens an asynchronous database session using `session_gen`.
        2. Passes the request, session, and additional data to the GraphQL resolver context.
        3. Executes the GraphQL operation using the provided schema and context.

    Returns:
        dict: The result of the GraphQL operation.
    """
    async with session_gen as session:
        success, result = await graphql(
            schema,
            data=await request.json(),
            context_value=context(request=request, db_session=session),
            **kwargs
        )

    return result


def create_graphql_route(
    resolvers: list,
    session_gen: SessionGenType,
    path_to_schema: str = "app/api/graphql/schema.graphql",
    graphql_server: Callable[..., Awaitable] = graphql_server,
    **kwargs
):
    """
    Create a FastAPI route for handling GraphQL requests.

    Args:
        resolvers (list): A list of resolvers for the GraphQL schema.
        session_gen (SessionGenType): A callable or generator function that provides
                                      an asynchronous database session.
        path_to_schema (str, optional): The path to the GraphQL schema definition file.
                                        Defaults to 'app/api/graphql/schema.graphql'.
        graphql_server (Callable[..., Awaitable], optional): The function to handle GraphQL requests.
                                                             Defaults to `graphql_server`.
        **kwargs: Additional arguments to customize the behavior of the route.

    Returns:
        Callable: An asynchronous FastAPI-compatible route handler.

    Workflow:
        1. Loads the schema definition from the provided file path.
        2. Creates an executable GraphQL schema using the provided resolvers.
        3. Returns an asynchronous route handler (`graphql_route`) that processes GraphQL requests.

    Example:
        app.add_api_route('/graphql', create_graphql_route(resolvers, get_session), methods=["POST"])
    """
    type_defs = load_schema_from_path(path_to_schema)
    schema = make_executable_schema(type_defs, resolvers)

    async def graphql_route(request: Request):
        return await graphql_server(request=request, schema=schema, session_gen=session_gen(), **kwargs)

    return graphql_route
