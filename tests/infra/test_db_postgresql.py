from unittest.mock import MagicMock

import pytest

from smartutils.error.sys import DatabaseError, LibraryUsageError


@pytest.fixture(scope="function")
async def setup_config(tmp_path_factory):
    config_str = """
postgresql:
  default:
    host: localhost
    port: 5432
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

    from smartutils.test import patched_manager_with_mocked_dbcli

    with patched_manager_with_mocked_dbcli(
        "smartutils.infra.db.postgresql.AsyncDBCli"
    ) as (
        MockDBCli,
        fake_session,
        instance,
    ):
        from smartutils.infra.db import postgresql

        assert isinstance(postgresql.AsyncDBCli, MagicMock)

        from smartutils.init import init

        await init(str(config_file))
        yield {
            "fake_session": fake_session,
            "MockDBCli": MockDBCli,
            "instance": instance,
        }


async def test_pgsql_manager_use_and_curr(setup_config):
    fake_session = setup_config["fake_session"]
    from smartutils.infra import PostgresqlManager

    pgsql_mgr = PostgresqlManager()

    @pgsql_mgr.use()
    async def biz():
        session = pgsql_mgr.curr
        assert session == fake_session
        return "ok"

    ret = await biz()
    assert ret == "ok"
    fake_session.commit.assert_awaited()

    # 异常回滚
    @pgsql_mgr.use()
    async def biz2():
        raise ValueError("fail")

    with pytest.raises(DatabaseError) as excinfo:
        await biz2()

    assert "fail" in str(excinfo.value)
    fake_session.rollback.assert_awaited()


async def test_curr_no_context(setup_config):
    from smartutils.infra import PostgresqlManager

    pgsql_mgr = PostgresqlManager()
    with pytest.raises(LibraryUsageError):
        pgsql_mgr.curr
