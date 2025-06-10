from unittest.mock import MagicMock

import pytest

from smartutils.error.sys import DatabaseError, LibraryUsageError


@pytest.fixture(scope="function")
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

    from smartutils.test import patched_manager_with_mocked_dbcli

    with patched_manager_with_mocked_dbcli("smartutils.infra.db.mysql.AsyncDBCli") as (
        MockDBCli,
        fake_session,
        instance,
    ):
        from smartutils.infra.db import mysql

        assert isinstance(mysql.AsyncDBCli, MagicMock)
        from smartutils.init import init

        await init(str(config_file))
        yield {
            "fake_session": fake_session,
            "MockDBCli": MockDBCli,
            "instance": instance,
        }


def test_optype_enum_values(setup_config):
    from smartutils.app.history import model

    assert model.OpType.ADD.value == 1
    assert model.OpType.DEL.value == 2
    assert model.OpType.UPDATE.value == 3


def test_ophistory_attributes(setup_config):
    from smartutils.app.history import model

    op = model.OpHistory(
        biz_type="test",
        biz_id=123,
        op_type=model.OpType.ADD.value,
        op_id=456,
        before_data={"foo": "bar"},
        after_data={"foo": "baz"},
        remark="test remark",
    )
    assert op.biz_type == "test"
    assert op.biz_id == 123
    assert op.op_type == 1
    assert op.op_id == 456
    assert op.before_data == {"foo": "bar"}
    assert op.after_data == {"foo": "baz"}
    assert op.remark == "test remark"
