import pytest

from smartutils.error.sys import DatabaseError, LibraryUsageError

# 不能在这儿import，setup_config中为防止单例影响，会先reset_all
# from smartutils.infra import MySQLManager


@pytest.fixture
async def setup_config(tmp_path_factory, mocker):
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

    from smartutils.call import mock_dbcli

    with mock_dbcli(mocker, "smartutils.infra.db.mysql.AsyncDBCli") as (
        MockDBCli,
        fake_session,
        instance,
    ):
        from smartutils.infra.db import mysql

        assert isinstance(mysql.AsyncDBCli, mocker.MagicMock)
        from smartutils.init import init

        init(str(config_file))
        yield {
            "fake_session": fake_session,
            "MockDBCli": MockDBCli,
            "instance": instance,
        }


async def test_mysql_manager_use_and_curr(setup_config):
    fake_session = setup_config["fake_session"]
    from smartutils.infra import MySQLManager

    mysql_mgr = MySQLManager()

    @mysql_mgr.use()
    async def biz():
        session = mysql_mgr.curr
        assert session == fake_session
        return "ok"

    ret = await biz()
    assert ret == "ok"
    fake_session.commit.assert_awaited()

    @mysql_mgr.use()
    async def biz2():
        raise ValueError("fail")

    with pytest.raises(DatabaseError) as excinfo:
        await biz2()
    assert "fail" in str(excinfo.value)
    fake_session.rollback.assert_awaited()


async def test_mysql_curr_no_context(setup_config):
    from smartutils.infra import MySQLManager

    mysql_mgr = MySQLManager()
    with pytest.raises(LibraryUsageError):
        mysql_mgr.curr
