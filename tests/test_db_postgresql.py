from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from smartutils.db import DB


@pytest.fixture(scope="session", autouse=True)
def setup_config(tmp_path_factory):
    config_str = """
postgresql:
  host: 192.168.1.56
  port: 3306
  user: root
  passwd: root
  db: testdb

  pool_size: 10
  max_overflow: 5
  pool_timeout: 30
  pool_recycle: 3600
  echo: false
  echo_pool: false
  connect_timeout: 10
  read_timeout: 10
  write_timeout: 10
  execute_timeout: 10"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    from smartutils.config import init
    init(str(config_file))
    print(config_file)

    from smartutils.db import init
    init()


@pytest.mark.asyncio
async def test_db_init_and_get_db():
    fake_engine = MagicMock()
    fake_engine.dispose = AsyncMock()
    fake_session = AsyncMock()
    fake_session.in_transaction = MagicMock(return_value=True)
    fake_session.__aenter__.return_value = fake_session
    fake_session.__aexit__.return_value = None

    with patch('smartutils.db.create_async_engine', return_value=fake_engine) as p_engine, \
            patch('smartutils.db.sessionmaker') as p_sessionmaker:
        p_sessionmaker.return_value = lambda: fake_session

        db = DB()
        assert db.engine == fake_engine

        # 测试 get_db 生成器
        agen = db.get_db()
        session = await agen.__anext__()
        assert session == fake_session
        await agen.aclose()
        await db.close()


@pytest.mark.asyncio
async def test_with_db_decorator():
    fake_engine = MagicMock()
    fake_engine.dispose = AsyncMock()
    fake_session = AsyncMock()
    fake_session.in_transaction = MagicMock(return_value=True)
    fake_session.commit = AsyncMock()
    fake_session.rollback = AsyncMock()
    fake_session.__aenter__.return_value = fake_session
    fake_session.__aexit__.return_value = None

    with patch('smartutils.db.create_async_engine', return_value=fake_engine), \
            patch('smartutils.db.sessionmaker') as p_sessionmaker:
        p_sessionmaker.return_value = lambda: fake_session
        db = DB()

        @db.with_db
        async def f():
            session = db.curr_db()
            assert session == fake_session
            return "ok"

        ret = await f()
        assert ret == "ok"
        fake_session.commit.assert_awaited()

        # 测试异常回滚
        @db.with_db
        async def f2():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            await f2()
        fake_session.rollback.assert_awaited()


@pytest.mark.asyncio
async def test_curr_db_no_context():
    db = DB()
    with pytest.raises(RuntimeError):
        db.curr_db()
