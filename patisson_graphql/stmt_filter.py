"""
SQLAlchemy Statement Builder with Logging

This module contains the `Stmt` class, which provides a fluent interface for constructing 
and filtering SQLAlchemy `Select` statements while maintaining a log of applied filters 
and operations.

Class:
------
Stmt:
    A wrapper around SQLAlchemy's `Select` statement that allows for easy filtering, ordering, 
    and limiting of queries. It also maintains a log of operations for debugging or tracing.

Methods:
--------
1. `__call__() -> Select`:
    Returns the current `Select` statement.

2. `log(pre: str = ' - ') -> str`:
    Returns a string representation of the statement's log, with each operation prefixed by `pre`.

3. Filtering Methods:
    - `lte_filter(column: Column, op: Optional[Any]) -> Self`: Adds a `<=` filter.
    - `gte_filter(column: Column, op: Optional[Any]) -> Self`: Adds a `>=` filter.
    - `lt_filter(column: Column, op: Optional[Any]) -> Self`: Adds a `<` filter.
    - `gt_filter(column: Column, op: Optional[Any]) -> Self`: Adds a `>` filter.
    - `eq_filter(column: Column, op: Optional[Any]) -> Self`: Adds a `==` filter.
    - `con_filter(column: Column, ops: Optional[Iterable[Any]]) -> Self`: Adds an `in` filter.
    - `not_con_filter(column: Column, ops: Optional[Iterable[Any]]) -> Self`: Adds a `not in` filter.
    - `con_model_filter(column: InstrumentedAttribute[Any], ops: Optional[Iterable[Any]]) -> Self`: 
      Adds an `in` filter for relationships.
    - `like_filter(column: Column, op: Optional[Any]) -> Self`: Adds a `LIKE` filter.
    - `where_filter(column: InstrumentedAttribute[Any], op: Optional[Any]) -> Self`: Adds a `WHERE` clause.

4. Ordering and Pagination:
    - `ordered_by(column: Optional[Column]) -> Self`: Adds an `ORDER BY` clause.
    - `limit(num: Optional[int]) -> Self`: Adds a `LIMIT` clause.
    - `offset(num: Optional[int]) -> Self`: Adds an `OFFSET` clause.

Attributes:
-----------
- `stmt` (Select): The underlying SQLAlchemy `Select` statement being built.
- `log_list` (list[str]): A list of strings representing the applied filters and operations.

Usage:
------
    from sqlalchemy import select, Column
    from your_module import Stmt

    query = select(User)
    stmt = Stmt(query)

    filtered_query = (
        stmt
        .gte_filter(User.age, 18)
        .lt_filter(User.age, 30)
        .ordered_by(User.name)
        .limit(10)
        .offset(0)
    )()

    print(stmt.log())
    # Output:
    # SELECT user.id, user.name, user.age FROM user
    #  - user.age >= 18
    #  - user.age < 30
    #  - order by name
    #  - limit 10
    #  - offset 0

"""

from collections.abc import Iterable
from typing import Any, Optional, Self

from sqlalchemy import Column, Select
from sqlalchemy.orm import InstrumentedAttribute


class Stmt:
    
    def __init__(self, stmt: Select) -> None:
        self.stmt = stmt
        self.log_list: list[str] = []
        
    def __call__(self) -> Select:
        return self.stmt 
    
    def log(self, pre: str = ' - ') -> str:
        log = str(self.stmt).split('\n', 1)[0] + '\n'
        for i in self.log_list:
            log += pre + i + '\n'
        return log
        
    def lte_filter(self, column: Column, op: Optional[Any]) -> Self:
        '<='
        if op: 
            self.stmt = self.stmt.filter(column <= op)
            self.log_list.append(f'{column.name} <= {op}')
        return self
        
    def gte_filter(self, column: Column, op: Optional[Any]) -> Self:
        '>='
        if op: 
            self.stmt = self.stmt.filter(column >= op)
            self.log_list.append(f'{column.name} >= {op}')
        return self
        
    def lt_filter(self, column: Column, op: Optional[Any]) -> Self:
        '<'
        if op: 
            self.stmt = self.stmt.filter(column < op)
            self.log_list.append(f'{column.name} < {op}')
        return self
      
    def gt_filter(self, column: Column, op: Optional[Any]) -> Self:
        '>'
        if op: 
            self.stmt = self.stmt.filter(column > op)
            self.log_list.append(f'{column.name} > {op}')
        return self
        
    def eq_filter(self, column: Column, op: Optional[Any]) -> Self:
        '=='
        if op: 
            self.stmt = self.stmt.filter(column == op)
            self.log_list.append(f'{column.name} == {op}')
        return self
       
    def con_filter(self, column: Column, ops: Optional[Iterable[Any]]) -> Self:
        'in'
        if ops: 
            self.stmt = self.stmt.filter(column.in_(ops))
            self.log_list.append(f'{column.name} in {ops}')
        return self
    
    def not_con_filter(self, column: Column, ops: Optional[Iterable[Any]]) -> Self:
        'not in'
        if ops: 
            self.stmt = self.stmt.filter(column.not_in(ops))
            self.log_list.append(f'{column.name} not in {ops}')
        return self
    
    def con_model_filter(self, column: InstrumentedAttribute[Any], ops: Optional[Iterable[Any]]) -> Self:
        '"in" for relationship'
        if ops:
            self.stmt = self.stmt.filter(column.any(column.property.mapper.class_.name.in_(ops)))
            self.log_list.append(f'{column.name} relationship in {ops}')
        return self    
    
    def like_filter(self, column: Column, op: Optional[Iterable[Any]]) -> Self:
        'LIKE'
        if op: 
            self.stmt = self.stmt.filter(column.like(op))
            self.log_list.append(f'{column.name} like {op}')
        return self
        
    def where_filter(self, column: InstrumentedAttribute[Any], op: Optional[Any]) -> Self:
        'WHERE'
        if op:
            self.stmt = self.stmt.where(column == op)
            self.log_list.append(f'{column.name} where {op}')
        return self
    
    def ordered_by(self, column: Optional[Column]) -> Self:
        if column is not None:
            self.stmt = self.stmt.order_by(column) 
            self.log_list.append(f'order by {column.name}')
        return self
    
    def limit(self, num: Optional[int]) -> Self:
        if num: 
            self.stmt = self.stmt.limit(num)
            self.log_list.append(f'limit {num}')
        return self    
    
    def offset(self, num: Optional[int]) -> Self:
        if num: 
            self.stmt = self.stmt.offset(num) 
            self.log_list.append(f'offset {num}')
        return self
    