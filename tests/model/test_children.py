import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

import smartutils.model.children as children_mod

Base = declarative_base()


class DummyModel(Base):
    __tablename__ = "dummy_model"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)


async def test_children_ids_basic():
    # 构造模拟数据: id, parent_id
    data = [
        {"id": 1, "parent_id": None},
        {"id": 2, "parent_id": 1},
        {"id": 3, "parent_id": 1},
        {"id": 4, "parent_id": 2},
        {"id": 5, "parent_id": 4},
    ]
    # 定义递归关系: 1 -> 2,3; 2 -> 4; 4 -> 5
    # 查找1的全部子（不含1），应为[2,3,4,5]（无序，但递归全查找）

    # mock session.execute 的返回
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [2, 3, 4, 5]
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    session_mock = AsyncMock()
    session_mock.execute.return_value = result_mock

    ids = await children_mod.children_ids(
        session_mock, DummyModel, DummyModel.id, DummyModel.parent_id, 1
    )
    assert set(ids) == {2, 3, 4, 5}


async def test_children_ids_leaf():
    # 根节点无子
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    session_mock = AsyncMock()
    session_mock.execute.return_value = result_mock

    ids = await children_mod.children_ids(
        session_mock, DummyModel, DummyModel.id, DummyModel.parent_id, 999
    )
    assert ids == []


async def test_children_ids_invalid():
    # root_id 不存在
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    session_mock = AsyncMock()
    session_mock.execute.return_value = result_mock

    ids = await children_mod.children_ids(
        session_mock, DummyModel, DummyModel.id, DummyModel.parent_id, None
    )
    assert ids == []
