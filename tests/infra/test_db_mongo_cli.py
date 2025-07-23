import pytest

import smartutils.infra.db.mongo_cli as mongomod
from smartutils.call import mock_module_absent
from smartutils.error.sys import LibraryUsageError


class DummyLogger:
    def exception(self, msg, **kwargs):
        # 记录异常行为
        DummyLogger.last = (msg, kwargs)

    def debug(self, *args, **kwargs):
        pass


DummyLogger.last = None


def dummy_async_func(*a, **k):
    DummyLogger.last = "called"
    return False


class DummyClient:
    def __init__(self):
        self.admin = self
        self.closed = False
        self.do_fail = False

    async def command(self, cmd):
        if cmd == "ping" and getattr(self, "do_fail", False):
            raise RuntimeError("failping")
        return "pong"

    def close(self):
        self.closed = True

    async def start_session(self):
        class DummySession:
            def __init__(self):
                self.closed = False

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                self.closed = True

            def start_transaction(self):
                self.active = True

        return DummySession()

    def __getitem__(self, name):  # 修复mock不能下标访问
        return DummyDB()


class DummyDB:
    pass


class DummyConf:
    url = "x"
    kw = {}
    db = "test"


@pytest.fixture
def c(mocker):
    mocker.patch.object(mongomod, "AsyncIOMotorClient", return_value=DummyClient())
    mocker.patch.object(mongomod, "AsyncIOMotorDatabase", DummyDB)
    c = mongomod.AsyncMongoCli(DummyConf(), "abc")
    yield c


async def test_ping_true_false(c):
    mongomod.logger = DummyLogger()  # 覆盖 logger
    assert await c.ping() is True
    c._client.do_fail = True
    assert await c.ping() is False
    assert DummyLogger.last[0].startswith("[{name}] MongoDB ping failed")


async def test_close(c):
    c._client.closed = False
    await c.close()
    assert c._client.closed is True


async def test_db_context_no_transaction(c):
    async with c.db(use_transaction=False) as (db, session):
        assert session is None
        assert isinstance(db, DummyDB)


async def test_db_context_use_transaction(c):
    # 必须再mock _client.start_session
    async with c.db(use_transaction=True) as (db, session):
        assert hasattr(session, "start_transaction") and hasattr(session, "closed")


async def test_assert_motor_not_installed(mocker):
    mock_module_absent(mocker, "motor")
    with pytest.raises(LibraryUsageError) as e:
        mongomod.AsyncMongoCli(DummyConf(), "abc")
    assert "depend on motor" in str(e.value)


async def test_mongo_db_commit_and_rollback():
    class DummySess:
        def __init__(self):
            self.committed = False
            self.aborted = False

        async def commit_transaction(self):
            self.committed = True

        async def abort_transaction(self):
            self.aborted = True

    db = None
    sess = DummySess()
    await mongomod.db_commit((db, sess))
    assert sess.committed is True
    await mongomod.db_rollback((db, sess))
    assert sess.aborted is True
    # 测试None不报错
    await mongomod.db_commit((db, None))
    await mongomod.db_rollback((db, None))
