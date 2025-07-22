import pytest

import smartutils.infra.mq.cli as mqmod


@pytest.fixture
def kafka_conf():
    class DummyConf:
        urls = ["localhost:9092"]
        kw = {}

    return DummyConf()


@pytest.fixture
def async_kafka_cli(mocker, kafka_conf):
    cli = mqmod.AsyncKafkaCli.__new__(mqmod.AsyncKafkaCli)
    cli._conf = kafka_conf
    cli._name = "test"
    cli._bootstrap_servers = kafka_conf.urls
    cli._producer = None
    cli._producer_lock = mocker.AsyncMock()
    return cli


async def test_start_producer_and_ping_success(mocker, async_kafka_cli, monkeypatch):
    fake_producer = mocker.AsyncMock()
    monkeypatch.setattr(
        mqmod, "AIOKafkaProducer", mocker.MagicMock(return_value=fake_producer)
    )
    monkeypatch.setattr(fake_producer, "start", mocker.AsyncMock())
    monkeypatch.setattr(fake_producer, "client", mocker.MagicMock())
    fake_producer.client.fetch_all_metadata = mocker.AsyncMock(return_value=True)
    monkeypatch.setattr(mqmod, "errors", mocker.MagicMock())
    async_kafka_cli._conf.kw = {}
    await async_kafka_cli._start_producer()
    async_kafka_cli._producer = fake_producer
    await async_kafka_cli.ping()
    fake_producer.client.fetch_all_metadata.assert_awaited()


async def test_start_producer_kafka_fail(mocker, async_kafka_cli, monkeypatch):
    fake_producer = mocker.AsyncMock()

    class DummyKafkaConn(Exception):
        pass

    errors = mocker.MagicMock()
    errors.KafkaConnectionError = DummyKafkaConn
    monkeypatch.setattr(
        mqmod, "AIOKafkaProducer", mocker.MagicMock(return_value=fake_producer)
    )
    monkeypatch.setattr(
        fake_producer, "start", mocker.AsyncMock(side_effect=DummyKafkaConn("fail"))
    )
    monkeypatch.setattr(fake_producer, "stop", mocker.AsyncMock())
    monkeypatch.setattr(mqmod, "errors", errors)
    async_kafka_cli._conf.kw = {}
    with pytest.raises(mqmod.MQError):
        await async_kafka_cli._start_producer()


async def test_send_data(mocker, async_kafka_cli, monkeypatch):
    fake_producer = mocker.AsyncMock()
    fake_producer.send_and_wait = mocker.AsyncMock()
    async_kafka_cli._producer = fake_producer
    monkeypatch.setattr(async_kafka_cli, "start_producer", mocker.AsyncMock())
    data = [{"x": 1}, {"y": 2}]
    await async_kafka_cli.send_data("t", data)
    assert fake_producer.send_and_wait.await_count == 2


async def test_close(mocker, async_kafka_cli):
    fake_producer = mocker.AsyncMock()
    async_kafka_cli._producer = fake_producer
    await async_kafka_cli.close()
    fake_producer.stop.assert_awaited()


async def test_consumer(mocker, async_kafka_cli, monkeypatch):
    fake_consumer = mocker.AsyncMock()
    monkeypatch.setattr(
        mqmod, "AIOKafkaConsumer", mocker.MagicMock(return_value=fake_consumer)
    )
    c = async_kafka_cli.consumer("t1", "gid", auto_offset_reset="earliest")
    assert c == fake_consumer


async def test_consume_kafka(mocker):
    cli = mocker.MagicMock()
    batcher = mqmod.KafkaBatchConsumer(cli, mocker.MagicMock(), "t1", "g1")
    msg = mocker.MagicMock()
    fake_consumer = mocker.AsyncMock()
    msgs = [msg, msg]

    async def fake_iter():
        for m in msgs:
            yield m

    fake_consumer.__aiter__.side_effect = fake_iter
    fake_consumer.start = mocker.AsyncMock()
    fake_consumer.stop = mocker.AsyncMock()
    await batcher._consume_kafka(fake_consumer)
    fake_consumer.start.assert_awaited()
    fake_consumer.stop.assert_awaited()
