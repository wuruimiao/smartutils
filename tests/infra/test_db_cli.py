import pytest

import smartutils.infra.db.sqlalchemy_cli as dbmod


@pytest.fixture
def dummy_conf():
    class Conf:
        url = "mysql+asyncmy://test"
        kw = {}

    return Conf()


@pytest.fixture
def dbcli(dummy_conf, mocker):
    # 避免实际构造engine，直接new并mock必要属性
    cli = dbmod.AsyncDBCli.__new__(dbmod.AsyncDBCli)
    cli._key = "test"
    cli._engine = mocker.AsyncMock()
    cli._session = mocker.MagicMock()
    return cli


async def test_db_ping_ok(dbcli, mocker):
    conn = mocker.AsyncMock()
    conn.execute = mocker.AsyncMock(return_value=True)
    mgr = mocker.MagicMock()
    mgr.__aenter__ = mocker.AsyncMock(return_value=conn)
    mgr.__aexit__ = mocker.AsyncMock(return_value=None)
    dbcli._engine.connect = mocker.MagicMock(return_value=mgr)
    assert await dbcli.ping() is True


async def test_db_ping_fail(dbcli, mocker):
    conn = mocker.AsyncMock()
    conn.execute = mocker.AsyncMock(return_value=True)
    mgr = mocker.MagicMock()
    mgr.__aenter__.side_effect = Exception("fail")
    mgr.__aexit__ = mocker.AsyncMock(return_value=None)
    dbcli._engine.connect = mocker.MagicMock(return_value=mgr)
    assert await dbcli.ping() is False


async def test_db_close(dbcli):
    await dbcli.close()
    dbcli._engine.dispose.assert_awaited()


async def test_session_ctx(dbcli, mocker):
    sess = mocker.AsyncMock()
    mgr = mocker.AsyncMock()
    mgr.__aenter__.return_value = sess
    mgr.__aexit__.return_value = None
    dbcli._session.return_value = mgr
    async with dbcli.db() as s:
        assert s == (sess, None)


def test_engine_property(dbcli):
    assert dbcli.engine == dbcli._engine


async def test_sqlalchemy_db_commit_and_rollback(mocker):
    sess = mocker.AsyncMock()
    transaction = mocker.MagicMock()
    transaction.commit = mocker.AsyncMock()
    transaction.rollback = mocker.AsyncMock()

    session_tuple = (sess, transaction)
    mocker.patch.object(dbmod, "logger", mocker.MagicMock())

    await dbmod.db_commit(session_tuple)
    transaction.commit.assert_awaited_once()

    await dbmod.db_rollback(session_tuple)
    transaction.rollback.assert_awaited_once()


def make_base():
    class DummyMeta:
        async def create_all(self, *args, **kwargs):
            return "created"

    class DummyBase:
        metadata = DummyMeta()

    return DummyBase


async def test_create_tables(dbcli, mocker):
    # 模拟 engine.begin 上下文管理器
    mgr = mocker.AsyncMock()

    async def dummy_run_sync(func):
        return await func(make_base().metadata)

    # mock engine.begin 返回管理器
    mgr.__aenter__.return_value = mocker.MagicMock(run_sync=dummy_run_sync)
    mgr.__aexit__.return_value = None
    dbcli.engine.begin = mocker.MagicMock(return_value=mgr)
    Base = make_base()
    await dbcli.create_tables([Base])


async def test_db_use_transaction(dbcli, mocker):
    """
    针对 use_transaction=True 的覆盖测试，保证事务 begin 流程被走到。
    """
    sess = mocker.AsyncMock()
    trans = mocker.AsyncMock()
    mgr = mocker.AsyncMock()
    # session.__aenter__ 返回 sess
    mgr.__aenter__.return_value = sess
    mgr.__aexit__.return_value = None
    # session.begin 返回 trans
    sess.begin = mocker.AsyncMock(return_value=trans)
    dbcli._session.return_value = mgr

    # mock session.begin 流程
    async with dbcli.db(use_transaction=True) as ctx:
        assert ctx == (sess, trans)
