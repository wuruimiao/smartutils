from unittest.mock import AsyncMock, MagicMock

import pytest

import smartutils.infra.db.sqlalchemy_cli as dbmod


@pytest.fixture
def dummy_conf():
    class Conf:
        url = "mysql+asyncmy://test"
        kw = {}

    return Conf()


@pytest.fixture
def dbcli(dummy_conf):
    # 避免实际构造engine，直接new并mock必要属性
    cli = dbmod.AsyncDBCli.__new__(dbmod.AsyncDBCli)
    cli._name = "test"
    cli._engine = AsyncMock()
    cli._session = MagicMock()
    return cli


async def test_ping_ok(dbcli):
    conn = AsyncMock()
    conn.execute = AsyncMock(return_value=True)
    mgr = MagicMock()
    mgr.__aenter__ = AsyncMock(return_value=conn)
    mgr.__aexit__ = AsyncMock(return_value=None)
    dbcli._engine.connect = MagicMock(return_value=mgr)
    assert await dbcli.ping() is True


async def test_ping_fail(dbcli, monkeypatch):
    conn = AsyncMock()
    conn.execute = AsyncMock(return_value=True)
    mgr = MagicMock()
    mgr.__aenter__.side_effect = Exception("fail")
    mgr.__aexit__ = AsyncMock(return_value=None)
    dbcli._engine.connect = MagicMock(return_value=mgr)
    assert await dbcli.ping() is False


async def test_close(dbcli):
    await dbcli.close()
    dbcli._engine.dispose.assert_awaited()


async def test_session_ctx(dbcli):
    sess = AsyncMock()
    mgr = AsyncMock()
    mgr.__aenter__.return_value = sess
    mgr.__aexit__.return_value = None
    dbcli._session.return_value = mgr
    async with dbcli.db() as s:
        assert s == (sess, None)


def test_engine_property(dbcli):
    assert dbcli.engine == dbcli._engine


# async def test_write_in_session(monkeypatch):
#     sess = MagicMock()
#     sess.new = {1}
#     sess.dirty = set()
#     sess.deleted = set()
#     sess.info = {}

#     # in_transaction 为 False
#     sess.in_transaction = lambda: False
#     monkeypatch.setattr(dbmod, "logger", MagicMock())
#     assert dbmod._write_in_session(sess) is True


async def test_db_commit_and_rollback(monkeypatch):
    sess = AsyncMock()
    transaction = MagicMock()
    transaction.commit = AsyncMock()
    transaction.rollback = AsyncMock()

    session_tuple = (sess, transaction)
    monkeypatch.setattr(dbmod, "logger", MagicMock())

    await dbmod.db_commit(session_tuple)
    transaction.commit.assert_awaited_once()

    await dbmod.db_rollback(session_tuple)
    transaction.rollback.assert_awaited_once()
