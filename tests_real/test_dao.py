from typing import Optional

import pytest
from pydantic import BaseModel
from sqlalchemy import Column, String, text
from sqlalchemy.orm import declarative_base

from smartutils.app.dao.base import DAODBase
from smartutils.app.dao.mixin import TimestampedMixin
from smartutils.error.sys import LibraryUsageError
from smartutils.for_test import ForTest

# 定义SQLAlchemy基础模型
Base = declarative_base()


class TModel(Base, TimestampedMixin):
    __tablename__ = "test_crud_base"
    name = Column(String(64), nullable=False)


# 定义Pydantic schema
class TCreateSchema(BaseModel):
    name: str


class TUpdateSchema(BaseModel):
    name: str
    foo: Optional[str] = None  # 用于测试 exclude_unset 行为，有默认但未提供时可被排除
    bar: Optional[str] = None  # 用于测试exclude by field行为


# DB初始化与销毁，由conftest或原有mysql fixture完成
@pytest.fixture
async def setup_test_table():
    from smartutils.infra import MySQLManager

    await MySQLManager().client().create_tables([Base])
    yield
    # 清理：删除表中所有测试数据
    mgr = MySQLManager()
    async with mgr.client().db() as session_tuple:
        session = session_tuple[0]
        await session.execute(text(f"DELETE FROM {TModel.__tablename__}"))
        await session.commit()


@pytest.fixture
async def crud():
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    return DAODBase[TModel, TCreateSchema, TUpdateSchema](TModel, mgr)


async def test_crud_create_and_get(crud, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        # 新增
        obj = await crud.create(TCreateSchema(name="foo"))
        await crud.db.curr.flush()
        assert obj.id > 0
        # get
        got = await crud.get(obj.id)
        assert got is not None and got.id == obj.id and got.name == "foo"
        # get(columns)
        got_tuple = await crud.get(obj.id, columns=[TModel.id, TModel.name])
        assert got_tuple == (obj.id, "foo")

    await biz()


async def test_crud_get_multi(crud, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        # 插入多条
        [await crud.create(TCreateSchema(name=f"bar{i}")) for i in range(3)]
        await crud.db.curr.flush()
        # get_multi默认
        records = await crud.get_multi()
        assert len(records) >= 3
        # get_multi有limit
        records_limit = await crud.get_multi(limit=2)
        assert len(records_limit) == 2
        # get_multi(columns)
        tups = await crud.get_multi(columns=[TModel.id, TModel.name])
        assert all(isinstance(t, tuple) and len(t) == 2 for t in tups)

    await biz()


async def test_crud_update(crud, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        obj = await crud.create(TCreateSchema(name="update_me"))
        await crud.db.curr.flush()
        # update（指定字段，指定filter）
        n = await crud.update(
            TUpdateSchema(name="updated"),
            [TModel.id == obj.id],
            update_fields=[TModel.name],
        )
        assert n == 1
        await crud.db.curr.flush()
        got = await crud.get(obj.id)
        assert got.name == "updated"

    await biz()


async def test_crud_update_unset_field_logger(mocker, crud, setup_test_table):
    ft = ForTest(mocker)

    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        obj = await crud.create(TCreateSchema(name="to_update"))
        await crud.db.curr.flush()
        # 调用update，仅name字段，foo（显式为None）不传，触发dump_removed逻辑
        await crud.update(
            TUpdateSchema(name="newval", bar="test"),
            [TModel.id == obj.id],
            update_fields=[TModel.name],
        )
        return obj.id

    _ = await biz()
    assert ft.assert_log("{} filtered out by unset: {}", "[DAODBase]", {"foo"})
    assert ft.assert_log("{} filtered out by fields: {}", "[DAODBase]", {"bar"})


async def test_crud_remove(crud, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        obj = await crud.create(TCreateSchema(name="for_remove"))
        await crud.db.curr.flush()
        n = await crud.remove([TModel.id == obj.id])
        assert n == 1
        await crud.db.curr.flush()
        got = await crud.get(obj.id)
        assert got is None

    await biz()


async def test_crud_update_no_filter_raises(crud, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        await crud.update(TUpdateSchema(name="fail"), [])

    with pytest.raises(LibraryUsageError) as e:
        await biz()
    assert (
        str(e.value)
        == "[DAODBase] filter_conditions cannot be empty to prevent updating the entire table!"
    )


async def test_crud_remove_no_filter_raises(crud, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        await crud.remove([])

    with pytest.raises(LibraryUsageError) as e:
        await biz()
    assert (
        str(e.value)
        == "[DAODBase] filter_conditions cannot be empty to prevent deleting the entire table!"
    )
