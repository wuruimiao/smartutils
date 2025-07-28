import pytest


def valid_kafka_conf(**kwargs):
    from smartutils.config.schema.host import HostConf

    return {
        "bootstrap_servers": [HostConf(host="127.0.0.1", port=9092)],
        "client_id": "test-client",
        "acks": "all",
        "compression_type": None,
        "max_batch_size": 16384,
        "linger_ms": 100,
        "request_timeout_ms": 5000,
        "retry_backoff_ms": 300,
        **kwargs,
    }


@pytest.fixture(scope="function")
async def setup_kafka_cli(tmp_path_factory, mocker):

    # mock aiokafka
    fake_producer = mocker.MagicMock()
    fake_producer.start = mocker.AsyncMock()
    fake_producer.stop = mocker.AsyncMock()
    fake_producer.client.fetch_all_metadata = mocker.AsyncMock()
    fake_producer.send_and_wait = mocker.AsyncMock()
    fake_consumer = mocker.MagicMock()
    fake_consumer.start = mocker.AsyncMock()
    fake_consumer.stop = mocker.AsyncMock()
    mocker.patch("smartutils.infra.mq.cli.AIOKafkaProducer", return_value=fake_producer)
    mocker.patch("smartutils.infra.mq.cli.AIOKafkaConsumer", return_value=fake_consumer)
    mocker.patch("smartutils.infra.mq.cli.TopicPartition", lambda t, p: (t, p))
    mocker.patch(
        "smartutils.infra.mq.cli.errors",
        mocker.MagicMock(KafkaConnectionError=Exception),
    )
    # 配置类 mock，跳过实际校验行为
    from smartutils.config.schema.kafka import KafkaConf

    kc = KafkaConf(**valid_kafka_conf())
    from smartutils.infra.mq.cli import AsyncKafkaCli

    cli = AsyncKafkaCli(kc, "test_cli")
    cli._producer = fake_producer

    yield cli, fake_producer, fake_consumer


async def test_ping_success(setup_kafka_cli):
    cli, fake_producer, _ = setup_kafka_cli
    ok = await cli.ping()
    assert ok
    fake_producer.client.fetch_all_metadata.assert_awaited()


async def test_ping_fail(setup_kafka_cli, mocker):
    cli, fake_producer, _ = setup_kafka_cli
    fake_producer.client.fetch_all_metadata.side_effect = Exception("netfail")
    logger_warn = mocker.patch("smartutils.infra.mq.cli.logger.warning")
    ok2 = await cli.ping()
    assert not ok2
    logger_warn.assert_called()


async def test_close(setup_kafka_cli):
    cli, fake_producer, _ = setup_kafka_cli
    await cli.close()
    fake_producer.stop.assert_awaited()


async def test_send_data(setup_kafka_cli):
    cli, fake_producer, _ = setup_kafka_cli
    await cli.send_data("topic", [{"k": 1}])
    fake_producer.send_and_wait.assert_awaited()


def test_consumer_create(setup_kafka_cli):
    cli, _, _ = setup_kafka_cli
    c = cli.consumer("mytopic", "gid", "earliest")
    assert c is not None


async def test_start_producer_error(mocker):
    from smartutils.config.schema.kafka import KafkaConf

    conf = KafkaConf(**valid_kafka_conf())

    from smartutils.infra.mq.cli import AsyncKafkaCli

    cli = AsyncKafkaCli(conf, "err")
    # 模拟 AIOKafkaProducer.start 失败
    fake_prod = mocker.MagicMock()
    fake_prod.start = mocker.AsyncMock(side_effect=Exception("failconn"))
    fake_prod.stop = mocker.AsyncMock()
    mocker.patch("smartutils.infra.mq.cli.AIOKafkaProducer", return_value=fake_prod)
    mocker.patch(
        "smartutils.infra.mq.cli.errors",
        mocker.MagicMock(KafkaConnectionError=Exception),
    )
    logger_exc = mocker.patch("smartutils.infra.mq.cli.logger.exception")
    with pytest.raises(Exception):
        await cli._start_producer()
    logger_exc.assert_called()
