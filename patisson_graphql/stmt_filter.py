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
    