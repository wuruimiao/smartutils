from unittest.mock import MagicMock, AsyncMock

import pytest

from smartutils.infra import MySQLManager


@pytest.fixture(scope="function", autouse=True)
async def setup_config(tmp_path_factory):
    config_str = """
mysql:
  default:
    host: localhost
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
    connect_timeout: 10
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

    from smartutils import init
    await init(str(config_file))

    yield

    from smartutils import reset_all
    await reset_all()


async def test_mysql_manager_use_and_curr(monkeypatch, setup_config):
    fake_session = AsyncMock()
    fake_session.in_transaction = MagicMock(return_value=True)
    fake_session.commit = AsyncMock()
    fake_session.rollback = AsyncMock()
    fake_session.__aenter__.return_value = fake_session
    fake_session.__aexit__.return_value = None

    fake_cli = MagicMock()
    fake_cli.session.return_value.__aenter__.return_value = fake_session
    fake_cli.session.return_value.__aexit__.return_value = None

    # Patch Manager的_resource字典
    mysql_mgr = MySQLManager()
    monkeypatch.setattr(mysql_mgr, "_resources", {"default": fake_cli})

    @mysql_mgr.use()
    async def biz():
        session = mysql_mgr.curr()
        assert session == fake_session
        return "ok"

    ret = await biz()
    assert ret == "ok"
    fake_session.commit.assert_awaited()

    # 异常回滚
    @mysql_mgr.use()
    async def biz2():
        raise ValueError("fail")

    with pytest.raises(RuntimeError):
        await biz2()
    fake_session.rollback.assert_awaited()


async def test_curr_no_context(setup_config):
    mysql_mgr = MySQLManager()
    with pytest.raises(RuntimeError):
        mysql_mgr.curr()
