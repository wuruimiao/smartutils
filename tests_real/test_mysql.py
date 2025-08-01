import pytest
from sqlalchemy import Column, Integer, String, insert, select
from sqlalchemy import delete as sql_delete
from sqlalchemy import update as sql_update
from sqlalchemy.orm import declarative_base

from smartutils.error.sys import DatabaseError, LibraryUsageError
from smartutils.infra.db.sqlalchemy_cli import db_commit, db_rollback

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64))


@pytest.fixture
async def setup_db():
    from smartutils.infra import MySQLManager

    my_mgr = MySQLManager()
    await my_mgr.client().create_tables([Base])
    yield


@pytest.fixture
async def setup_unreachable_db(tmp_path_factory: pytest.TempPathFactory):
    config_str = """
mysql:
  default:
    host: 222.222.222.222
    port: 3306
    user: root
    passwd: naobo
    db: test_db
    pool_size: 10
    max_overflow: 5
    pool_timeout: 30
    pool_recycle: 3600
    echo: false
    echo_pool: false
    connect_timeout: 1
    execute_timeout: 10
project:
  name: auth
  id: 0
  description: test_auth
  version: 0.0.1
  key: test_key"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)
    from smartutils.init import reset_all

    await reset_all()
    from smartutils.init import init

    init(str(config_file))

    yield


async def test_mysql_manager_no_confs():
    from smartutils.init import reset_all

    await reset_all()
    from smartutils.infra import MySQLManager

    with pytest.raises(LibraryUsageError):
        MySQLManager()


async def test_mysql_session_insert_query(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    async with mgr.session() as session:
        session = session[0]
        stmt = insert(User).values(name="SessionUser1")
        result = await session.execute(stmt)
        await session.commit()
        assert result.inserted_primary_key
        user_id = result.inserted_primary_key[0]
        stmt = select(User).where(User.id == user_id)
        user = (await session.execute(stmt)).scalar_one()
        assert user.name == "SessionUser1"  # type: ignore
        await session.execute(sql_delete(User).where(User.id == user_id))
        await session.commit()


async def test_mysql_session_update_commit(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    async with mgr.session() as _session:
        session = _session[0]
        result = await session.execute(insert(User).values(name="SessionUpdate"))
        await session.commit()
        assert result.inserted_primary_key
        user_id = result.inserted_primary_key[0]
        upd = sql_update(User).where(User.id == user_id).values(name="AfterUpdate")
        await session.execute(upd)
        await db_commit(_session)
        new_name = (
            await session.execute(select(User.name).where(User.id == user_id))
        ).scalar_one()
        assert new_name == "AfterUpdate"
        await session.execute(sql_delete(User).where(User.id == user_id))
        await session.commit()


async def test_mysql_session_update_rollback(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    async with mgr.session() as _session:
        session = _session[0]
        result = await session.execute(insert(User).values(name="RollbackTest"))
        await session.commit()
        assert result.inserted_primary_key
        user_id = result.inserted_primary_key[0]
        upd = sql_update(User).where(User.id == user_id).values(name="ShouldRollback")
        await session.execute(upd)
        await db_rollback(_session)
        name = (
            await session.execute(select(User.name).where(User.id == user_id))
        ).scalar_one()
        assert name == "RollbackTest"
        await session.execute(sql_delete(User).where(User.id == user_id))
        await session.commit()


async def test_mysql_session_delete(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    async with mgr.session() as session:
        session = session[0]
        result = await session.execute(insert(User).values(name="DeleteTest"))
        await session.commit()
        assert result.inserted_primary_key
        user_id = result.inserted_primary_key[0]
        await session.execute(sql_delete(User).where(User.id == user_id))
        await session.commit()
        res = await session.execute(select(User).where(User.id == user_id))
        user = res.scalar_one_or_none()
        assert user is None


async def test_mysql_cli_ping(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    cli = mgr.client()
    assert await cli.ping() is True


async def test_mysql_cli_close(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    cli = mgr.client()
    await cli.close()


async def test_mysql_create(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use()
    async def create():
        insert_stmt = insert(User).values(name="TestUser")
        result = await mgr.curr.execute(insert_stmt)
        await mgr.curr.commit()
        assert result.inserted_primary_key
        return result.inserted_primary_key[0]

    user_id = await create()
    assert isinstance(user_id, int) and user_id > 0


async def test_mysql_read(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use()
    async def create():
        insert_stmt = insert(User).values(name="UserRead")
        result = await mgr.curr.execute(insert_stmt)
        await mgr.curr.commit()
        assert result.inserted_primary_key
        return result.inserted_primary_key[0]

    user_id = await create()

    @mgr.use()
    async def read():
        stmt = select(User).where(User.id == user_id)
        result = await mgr.curr.execute(stmt)
        user = result.scalar_one()
        assert user.name == "UserRead"  # type: ignore

    await read()


async def test_mysql_update(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use()
    async def create():
        insert_stmt = insert(User).values(name="UserUpdate")
        result = await mgr.curr.execute(insert_stmt)
        await mgr.curr.commit()
        assert result.inserted_primary_key
        return result.inserted_primary_key[0]

    user_id = await create()

    @mgr.use()
    async def update():
        upd_stmt = sql_update(User).where(User.id == user_id).values(name="UpdatedUser")
        await mgr.curr.execute(upd_stmt)
        await mgr.curr.commit()
        stmt = select(User).where(User.id == user_id)
        result = await mgr.curr.execute(stmt)
        user = result.scalar_one()
        assert user.name == "UpdatedUser"  # type: ignore

    await update()


async def test_mysql_delete(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use()
    async def create():
        insert_stmt = insert(User).values(name="UserDelete")
        result = await mgr.curr.execute(insert_stmt)
        await mgr.curr.commit()
        assert result.inserted_primary_key
        return result.inserted_primary_key[0]

    user_id = await create()

    @mgr.use()
    async def delete_and_check():
        del_stmt = sql_delete(User).where(User.id == user_id)
        await mgr.curr.execute(del_stmt)
        await mgr.curr.commit()
        stmt = select(User).where(User.id == user_id)
        result = await mgr.curr.execute(stmt)
        user = result.scalar_one_or_none()
        assert user is None

    await delete_and_check()


async def test_mysql_cli_ping_fail(setup_unreachable_db: None):
    from smartutils.infra import MySQLManager

    cli = MySQLManager().client()
    # ping 不可用时直接返回False不抛出
    assert await cli.ping() is False


async def test_mysql_cli_create_tables_fail(setup_unreachable_db: None):
    from smartutils.infra import MySQLManager

    cli = MySQLManager().client()
    # 尝试 create_tables 触发连接异常
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()
    with pytest.raises(Exception):
        await cli.create_tables([Base])


async def test_mysql_manager_session_unreachable(setup_unreachable_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    with pytest.raises(Exception):
        async with mgr.session() as session:
            session = session[0]
            # 实际执行一次SQL，才能确保抛出连接异常
            await session.execute(select(User))


async def test_mysql_manager_use_unreachable(setup_unreachable_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()

    @mgr.use()
    async def demo():
        from sqlalchemy import select

        await mgr.curr.execute(select(User))

    with pytest.raises(DatabaseError):
        await demo()


async def test_mysql_use_with_transaction_auto_rollback(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    test_name = "TransAutoRollback"

    @mgr.use(use_transaction=True)
    async def insert_but_raise():
        stmt = insert(User).values(name=test_name)
        await mgr.curr.execute(stmt)
        # 此时未commit，模拟异常触发rollback
        raise RuntimeError("trigger rollback")

    # 触发rollback
    try:
        await insert_but_raise()
    except DatabaseError:
        ...

    # 检查数据应不存在
    @mgr.use()
    async def check():
        stmt = select(User).where(User.name == test_name)
        user = (await mgr.curr.execute(stmt)).scalar_one_or_none()
        assert user is None

    await check()


async def test_mysql_use_with_transaction_commit(setup_db: None):
    from smartutils.infra import MySQLManager

    mgr = MySQLManager()
    test_name = "TransCommit"

    @mgr.use(use_transaction=True)
    async def do_insert_and_commit():
        stmt = insert(User).values(name=test_name)
        result = await mgr.curr.execute(stmt)
        await mgr.curr.flush()
        assert result.inserted_primary_key
        return result.inserted_primary_key[0]

    user_id = await do_insert_and_commit()

    @mgr.use()
    async def check():
        stmt = select(User).where(User.id == user_id)
        user = (await mgr.curr.execute(stmt)).scalar_one_or_none()
        assert user is not None and user.name == test_name  # type: ignore

    await check()

    # 清理
    @mgr.use()
    async def cleanup():
        await mgr.curr.execute(sql_delete(User).where(User.id == user_id))
        await mgr.curr.commit()

    await cleanup()
