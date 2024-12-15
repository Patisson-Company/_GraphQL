# Patisson GraphQL

**Patisson GraphQL** is a library designed to simplify the setup and integration of microservices that need to serve GraphQL responses. It provides utilities for handling GraphQL queries, constructing SQLAlchemy queries, and managing context and schema in frameworks like FastAPI. The library is modular and extensible, allowing seamless expansion to other frameworks in the future.

---

## Installation

```bash
pip install git+https://github.com/Patisson-Company/_GraphQL
```

## Features

- **GraphQL Query Handling**: Utilities for efficiently resolving GraphQL queries using Ariadne.
- **SQLAlchemy Statement Builder**: A fluent interface for constructing and logging SQLAlchemy `Select` statements.
- **Selected Fields Mapper**: Automatically maps selected GraphQL fields to SQLAlchemy model attributes.
- **Framework Integration**: Tools for FastAPI to quickly set up GraphQL endpoints, with plans for additional frameworks in future versions.

---

## Structure

### 1. **`framework_utils` Package**
Utilities tailored for specific frameworks. Currently, only FastAPI is supported.

- **`fastapi.py`**:
  - Functions and classes to set up GraphQL endpoints with FastAPI using Ariadne.
  - Includes schema loading, resolver injection, and customizable context handling.
  - Example Usage:
    ```python
    from fastapi import FastAPI
    from patisson_graphql.framework_utils.fastapi import create_graphql_route, resolvers, get_session

    app = FastAPI()

    app.add_api_route(
        "/graphql",
        create_graphql_route(resolvers=resolvers, session_gen=get_session)
    )
    ```

### 2. **`stmt_filter.py`**
A utility for building SQLAlchemy `Select` statements with an intuitive, chainable API and integrated logging.

- **`Stmt` Class**:
  - Fluent methods for filtering, ordering, limiting, and offsetting queries.
  - Keeps track of all applied operations for debugging and traceability.
  - Example Usage:
    ```python
    from patisson_graphql.stmt_filter import Stmt
    from sqlalchemy import select

    stmt = Stmt(select(User))
    filtered_stmt = (
        stmt
        .gte_filter(User.age, 18)
        .lt_filter(User.age, 30)
        .ordered_by(User.name)
        .limit(10)
    )()
    print(stmt.log())
    ```

### 3. **`selected_fields.py`**
A utility to extract the selected fields from a GraphQL query and map them to SQLAlchemy model attributes.

- **`selected_fields` Function**:
  - Converts GraphQL `info` objects into a list of SQLAlchemy model attributes.
  - Example Usage:
    ```python
    from patisson_graphql.selected_fields import selected_fields

    fields = selected_fields(info, User)
    ```
