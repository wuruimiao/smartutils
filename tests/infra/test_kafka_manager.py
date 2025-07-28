import pytest


@pytest.fixture(scope="function")
async def setup_kafka_config(tmp_path_factory, mocker):
    config_str = """
kafka:
  default:
    bootstrap_servers:
      - host: localhost
        port: 9092
    client_id: pytest-client-id
    acks: all
    compression_type: zstd
    max_batch_size: 16384
    linger_ms: 0
    request_timeout_ms: 1000
    retry_backoff_ms: 100
project:
  name: smartutils_test
  id: 1
  description: kafka test
  version: 1.0.0
  key: test_key
"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_kafka_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    from smartutils.infra.mq.cli import AsyncKafkaCli

    mocker.patch.object(AsyncKafkaCli, "start_producer", return_value=1)

    from smartutils.init import init

    init(str(config_file))
    yield


async def test_kafka_manager_use_and_curr(setup_kafka_config):
    from smartutils.infra.mq.kafka import KafkaManager

    kafka_mgr = KafkaManager()

    # 正常分支
    @kafka_mgr.use()
    async def biz():
        session = kafka_mgr.curr  # noqa: F841
        return "ok"

    ret = await biz()
    assert ret == "ok"

    # 异常分支
    @kafka_mgr.use()
    async def error_func():
        raise ValueError("fail")

    from smartutils.error.sys import MQError

    with pytest.raises(MQError) as excinfo:
        await error_func()
    assert "fail" in str(excinfo.value)


async def test_kafka_curr_no_ctx(setup_kafka_config):
    from smartutils.error.sys import LibraryUsageError
    from smartutils.infra.mq.kafka import KafkaManager

    kafka_mgr = KafkaManager()
    with pytest.raises(LibraryUsageError):
        kafka_mgr.curr
