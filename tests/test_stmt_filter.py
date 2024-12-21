import pytest
from sqlalchemy import Column, Integer, MetaData, String, select
from sqlalchemy.orm import declarative_base

from patisson_graphql.stmt_filter import Stmt

Base = declarative_base()
metadata = MetaData()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)


@pytest.fixture
def stmt():
    query = select(User)
    return Stmt(query)


def test_lte_filter(stmt: Stmt):
    stmt.lte_filter(User.age, 30)
    assert 'age <= 30' in stmt.log_list


def test_gte_filter(stmt: Stmt):
    stmt.gte_filter(User.age, 18)
    assert 'age >= 18' in stmt.log_list


def test_lt_filter(stmt: Stmt):
    stmt.lt_filter(User.age, 25)
    assert 'age < 25' in stmt.log_list


def test_gt_filter(stmt: Stmt):
    stmt.gt_filter(User.age, 20)
    assert 'age > 20' in stmt.log_list


def test_eq_filter(stmt: Stmt):
    stmt.eq_filter(User.name, 'John')
    assert 'name == John' in stmt.log_list


def test_con_filter(stmt: Stmt):
    stmt.con_filter(User.age, [18, 25, 30])
    assert 'age in [18, 25, 30]' in stmt.log_list


def test_not_con_filter(stmt: Stmt):
    stmt.not_con_filter(User.age, [18, 25, 30])
    assert 'age not in [18, 25, 30]' in stmt.log_list


def test_like_filter(stmt: Stmt):
    stmt.like_filter(User.name, '%John%')
    assert 'name like %John%' in stmt.log_list


def test_where_filter(stmt: Stmt):
    stmt.where_filter(User.age, 25)
    assert 'age where 25' in stmt.log_list


def test_ordered_by(stmt: Stmt):
    stmt.ordered_by(User.name)
    assert 'order by name' in stmt.log_list


def test_limit(stmt: Stmt):
    stmt.limit(10)
    assert 'limit 10' in stmt.log_list


def test_offset(stmt: Stmt):
    stmt.offset(5)
    assert 'offset 5' in stmt.log_list
