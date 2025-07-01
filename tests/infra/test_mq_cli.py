from unittest.mock import AsyncMock, MagicMock

import pytest

import smartutils.infra.mq.cli as mqmod


@pytest.fixture
def kafka_conf():
    class DummyConf:
        urls = ["localhost:9092"]
        kw = {}

    return DummyConf()


@pytest.fixture
def async_kafka_cli(kafka_conf):
    cli = mqmod.AsyncKafkaCli.__new__(mqmod.AsyncKafkaCli)
    cli._conf = kafka_conf
    cli._name = "test"
    cli._bootstrap_servers = kafka_conf.urls
    cli._producer = None
    cli._producer_lock = AsyncMock()
    return cli


async def test_start_producer_and_ping_success(monkeypatch, async_kafka_cli):
    fake_producer = AsyncMock()
    monkeypatch.setattr(
        mqmod, "AIOKafkaProducer", MagicMock(return_value=fake_producer)
    )
    monkeypatch.setattr(fake_producer, "start", AsyncMock())
    monkeypatch.setattr(fake_producer, "client", MagicMock())
    fake_producer.client.fetch_all_metadata = AsyncMock(return_value=True)
    monkeypatch.setattr(mqmod, "errors", MagicMock())
    async_kafka_cli._conf.kw = {}
    await async_kafka_cli._start_producer()  # 仅校正常
    async_kafka_cli._producer = fake_producer
    await async_kafka_cli.ping()
    fake_producer.client.fetch_all_metadata.assert_awaited()


async def test_start_producer_kafka_fail(monkeypatch, async_kafka_cli):
    fake_producer = AsyncMock()

    class DummyKafkaConn(Exception):
        pass

    errors = MagicMock()
    errors.KafkaConnectionError = DummyKafkaConn
    monkeypatch.setattr(
        mqmod, "AIOKafkaProducer", MagicMock(return_value=fake_producer)
    )
    monkeypatch.setattr(
        fake_producer, "start", AsyncMock(side_effect=DummyKafkaConn("fail"))
    )
    monkeypatch.setattr(fake_producer, "stop", AsyncMock())
    monkeypatch.setattr(mqmod, "errors", errors)
    async_kafka_cli._conf.kw = {}
    with pytest.raises(mqmod.MQError):
        await async_kafka_cli._start_producer()


async def test_send_data(async_kafka_cli, monkeypatch):
    fake_producer = AsyncMock()
    fake_producer.send_and_wait = AsyncMock()
    async_kafka_cli._producer = fake_producer
    monkeypatch.setattr(async_kafka_cli, "start_producer", AsyncMock())
    # 单条/多条
    data = [{"x": 1}, {"y": 2}]
    await async_kafka_cli.send_data("t", data)
    assert fake_producer.send_and_wait.await_count == 2


async def test_close(async_kafka_cli):
    fake_producer = AsyncMock()
    async_kafka_cli._producer = fake_producer
    await async_kafka_cli.close()
    fake_producer.stop.assert_awaited()


async def test_consumer(monkeypatch, async_kafka_cli):
    fake_consumer = AsyncMock()
    monkeypatch.setattr(
        mqmod, "AIOKafkaConsumer", MagicMock(return_value=fake_consumer)
    )
    c = async_kafka_cli.consumer("t1", "gid", auto_offset_reset="earliest")
    assert c == fake_consumer


async def test_consume_kafka(monkeypatch):
    # 验证消费流程、stop被调用
    cli = MagicMock()
    batcher = mqmod.KafkaBatchConsumer(cli, MagicMock(), "t1", "g1")
    msg = MagicMock()
    fake_consumer = AsyncMock()
    msgs = [msg, msg]

    async def fake_iter():
        for m in msgs:
            yield m

    fake_consumer.__aiter__.side_effect = fake_iter
    fake_consumer.start = AsyncMock()
    fake_consumer.stop = AsyncMock()
    await batcher._consume_kafka(fake_consumer)
    fake_consumer.start.assert_awaited()
    fake_consumer.stop.assert_awaited()
