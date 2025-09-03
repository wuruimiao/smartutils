import sys
from typing import Optional

import pytest
from pydantic import BaseModel
from sqlalchemy import Column, String, text
from sqlalchemy.orm import declarative_base

from smartutils.app.dao.base import DAOBase
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


class TDao(DAOBase[TModel, TCreateSchema, TUpdateSchema]): ...


@pytest.fixture
async def dao():
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    return TDao(TModel, mgr)


async def test_crud_create_and_get(dao, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        # 新增
        obj = await dao.create(TCreateSchema(name="foo"))
        await dao.db.curr.flush()
        assert obj.id > 0
        # get
        got = await dao.get(obj.id)
        assert got is not None and got.id == obj.id and got.name == "foo"
        # get(columns)
        got_tuple = await dao.get(obj.id, columns=[TModel.id, TModel.name])
        assert got_tuple == (obj.id, "foo")

    await biz()


async def test_crud_get_multi(dao, setup_test_table, mocker):
    from smartutils.infra import MySQLManager

    ft = ForTest(mocker)
    mgr = MySQLManager()

    @mgr.use
    async def biz():
        # 插入多条
        [await dao.create(TCreateSchema(name=f"bar{i}")) for i in range(3)]
        await dao.db.curr.flush()
        # get_multi默认
        records = await dao.get_multi()
        assert len(records) >= 3

        # get_multi有limit
        records_limit = await dao.get_multi(limit=2)
        assert len(records_limit) == 2

        # 跳过3条，应无数据
        records_limit = await dao.get_multi(limit=2, skip=3)
        assert len(records_limit) == 0

        # 排序
        records_order = await dao.get_multi(order_by=[TModel.id.desc()])
        assert all(
            records_order[i].id >= records_order[i + 1].id
            for i in range(len(records_order) - 1)
        )

        # last_id分页
        records_last_id = await dao.get_multi(
            order_by=[TModel.id.desc()], last_id=3, limit=1
        )
        assert len(records_last_id) == 1 and records_last_id[0].id >= 3

        # skip，last_id共用，last_id生效
        records_skip_last_id = await dao.get_multi(
            order_by=[TModel.id.desc()], last_id=sys.maxsize, limit=1, skip=0
        )
        assert len(records_skip_last_id) == 0

        # get_multi(columns)
        tups = await dao.get_multi(columns=[TModel.id, TModel.name])
        assert all(isinstance(t, tuple) and len(t) == 2 for t in tups)

    await biz()
    ft.assert_log("{} get_multi use last_id, ignore skip.", "[TDao]")


async def test_crud_update(dao, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        obj = await dao.create(TCreateSchema(name="update_me"))
        await dao.db.curr.flush()
        # update（指定字段，指定filter）
        n = await dao.update(
            TUpdateSchema(name="updated"),
            [TModel.id == obj.id],
            update_fields=[TModel.name],
        )
        assert n == 1
        await dao.db.curr.flush()
        got = await dao.get(obj.id)
        assert got.name == "updated"

    await biz()


async def test_crud_update_unset_field_logger(mocker, dao, setup_test_table):
    ft = ForTest(mocker)

    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        obj = await dao.create(TCreateSchema(name="to_update"))
        await dao.db.curr.flush()
        # 调用update，仅name字段，foo（显式为None）不传，触发dump_removed逻辑
        await dao.update(
            TUpdateSchema(name="newval", bar="test"),
            [TModel.id == obj.id],
            update_fields=[TModel.name],
        )
        return obj.id

    _ = await biz()
    ft.assert_log("{} filtered out by unset: {}", "[TDao]", {"foo"})
    ft.assert_log("{} filtered out by fields: {}", "[TDao]", {"bar"})


async def test_crud_remove(dao, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        obj = await dao.create(TCreateSchema(name="for_remove"))
        await dao.db.curr.flush()
        n = await dao.remove([TModel.id == obj.id])
        assert n == 1
        await dao.db.curr.flush()
        got = await dao.get(obj.id)
        assert got is None

    await biz()


async def test_crud_update_no_filter_raises(dao, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        await dao.update(TUpdateSchema(name="fail"), [])

    with pytest.raises(LibraryUsageError) as e:
        await biz()
    assert (
        str(e.value)
        == "[TDao] filter_conditions cannot be empty to prevent updating the entire table!"
    )


async def test_crud_remove_no_filter_raises(dao, setup_test_table):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use
    async def biz():
        await dao.remove([])

    with pytest.raises(LibraryUsageError) as e:
        await biz()
    assert (
        str(e.value)
        == "[TDao] filter_conditions cannot be empty to prevent deleting the entire table!"
    )
