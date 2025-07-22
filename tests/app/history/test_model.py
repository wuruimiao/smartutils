import pytest


@pytest.fixture(scope="function")
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
        print(">>> setup_config: start fixture patch/db generation")
        from smartutils.infra.db import mysql

        assert isinstance(mysql.AsyncDBCli, mocker.MagicMock)
        from smartutils.init import init

        init(str(config_file))
        yield {
            "fake_session": fake_session,
            "MockDBCli": MockDBCli,
            "instance": instance,
        }


def test_optype_enum_values(setup_config):
    from smartutils.app.history import OpType

    assert OpType.ADD.value == 1
    assert OpType.DEL.value == 2
    assert OpType.UPDATE.value == 3


def test_ophistory_attributes(setup_config):
    from smartutils.app.history import OpHistory, OpType

    op = OpHistory(
        biz_type="test",
        biz_id=123,
        op_type=OpType.ADD.value,
        op_id=456,
        before_data={"foo": "bar"},
        after_data={"foo": "baz"},
        remark="test remark",
    )
    assert op.biz_type == "test"  # type: ignore
    assert op.biz_id == 123  # type: ignore
    assert op.op_type == 1  # type: ignore
    assert op.op_id == 456  # type: ignore
    assert op.before_data == {"foo": "bar"}  # type: ignore
    assert op.after_data == {"foo": "baz"}  # type: ignore
    assert op.remark == "test remark"  # type: ignore
