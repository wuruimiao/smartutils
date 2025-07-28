import asyncio

import pytest

import smartutils.infra.mq.cli as mq_cli
from smartutils.infra.mq.cli import AsyncKafkaCli, KafkaBatchConsumer


async def test_kafka_batch_consumer_start_stop(mocker):
    # 构造fake consumer和kafka_cli
    fake_consumer = mocker.Mock()
    fake_consumer.start = mocker.AsyncMock()
    fake_consumer.stop = mocker.AsyncMock()
    fake_consumer.commit = mocker.AsyncMock()
    fake_consumer.__aiter__ = lambda s: iter([])
    fake_kafka_cli = mocker.Mock(spec=AsyncKafkaCli)
    fake_kafka_cli.consumer.return_value = fake_consumer

    process_func = mocker.AsyncMock()
    consumer = KafkaBatchConsumer(
        kafka_cli=fake_kafka_cli,
        process_func=process_func,
        topic="topic",
        group_id="gid",
        batch_size=2,
        timeout=0.1,
    )

    task = asyncio.create_task(consumer.start())
    await asyncio.sleep(0.05)
    await consumer.stop()
    await asyncio.sleep(0.05)
    task.cancel()
    assert isinstance(consumer.queue, asyncio.Queue)
    fake_consumer.start.assert_awaited()
    fake_consumer.stop.assert_awaited()


async def test_kafka_batch_consumer_process(mocker):
    # 1. 构造消息对象
    FakeMsg = mocker.Mock
    msg1 = FakeMsg()
    msg1.value = b"hi1"
    msg1.topic = "t"
    msg1.partition = 0
    msg1.offset = 10
    msg2 = FakeMsg()
    msg2.value = b"hi2"
    msg2.topic = "t"
    msg2.partition = 0
    msg2.offset = 11

    # 2. fake consumer
    fake_consumer = mocker.Mock()
    fake_consumer.commit = mocker.AsyncMock()
    # 3. fake_kafka_cli
    fake_kafka_cli = mocker.Mock(spec=AsyncKafkaCli)
    fake_kafka_cli.consumer.return_value = fake_consumer

    # 4. 检查消息处理被调用
    process_func = mocker.AsyncMock()

    consumer = KafkaBatchConsumer(
        kafka_cli=fake_kafka_cli,
        process_func=process_func,
        topic="topic",
        group_id="gid",
        batch_size=2,
        timeout=0.1,
    )

    # 队列填充模拟
    await consumer.queue.put(msg1)
    await consumer.queue.put(msg2)
    # 运行一个小步
    run_task = asyncio.create_task(consumer._process_batch(fake_consumer))
    await asyncio.sleep(0.15)
    consumer._should_stop.set()
    await asyncio.sleep(0.05)
    run_task.cancel()

    process_func.assert_awaited()
    fake_consumer.commit.assert_awaited()


async def test_batch_consumer_process_timeout(mocker):
    # timeout分支（148-149）
    fake_consumer = mocker.Mock()
    fake_consumer.commit = mocker.AsyncMock()
    fake_kafka_cli = mocker.Mock()
    fake_kafka_cli.consumer.return_value = fake_consumer
    process_func = mocker.AsyncMock()
    consumer = KafkaBatchConsumer(
        kafka_cli=fake_kafka_cli,
        process_func=process_func,
        topic="t",
        group_id="gid",
        batch_size=2,
        timeout=0.01,
    )
    # 用单条消息后触发等待超时
    msg = mocker.Mock()
    msg.value = b"x"
    msg.topic = "t"
    msg.partition = 0
    msg.offset = 1
    await consumer.queue.put(msg)
    run_task = asyncio.create_task(consumer._process_batch(fake_consumer))
    await asyncio.sleep(0.05)
    consumer._should_stop.set()
    await asyncio.sleep(0.01)
    run_task.cancel()
    process_func.assert_awaited()


async def test_start_producer_kafka_conn_ok(mocker):
    from smartutils.config.schema.kafka import KafkaConf

    conf = KafkaConf(
        bootstrap_servers=[{"host": "1.2.3.4", "port": 9092}], client_id="u", acks="all"
    )
    cli = AsyncKafkaCli(conf, "test-ok")
    fake_prod = mocker.MagicMock()
    fake_prod.start = mocker.AsyncMock()
    fake_prod.stop = mocker.AsyncMock()
    mocker.patch.object(mq_cli, "AIOKafkaProducer", return_value=fake_prod)

    fake_prod.start.return_value = 1
    await cli._start_producer()


async def test_consume_kafka_queue_put(mocker):
    # 准备 KafkaBatchConsumer 相关 mock 依赖
    fake_kafka_cli = mocker.MagicMock()
    fake_process_func = mocker.AsyncMock()
    consumer = mocker.MagicMock()
    consumer.start = mocker.AsyncMock()
    consumer.stop = mocker.AsyncMock()

    # 构造异步generator模仿 async for msg in consumer
    class FakeMsg:
        topic = "t"
        partition = 0
        offset = 1
        value = b"data"

    async def msg_iter(self):
        # 返回1条消息后结束
        yield FakeMsg()

    consumer.__aiter__ = msg_iter

    # 实例化 KafkaBatchConsumer
    batcher = mq_cli.KafkaBatchConsumer(
        kafka_cli=fake_kafka_cli,
        process_func=fake_process_func,
        topic="test",
        group_id="gid",
        batch_size=3,
        timeout=1,
    )

    # 执行 _consume_kafka 方法，覆盖 queue.put
    await batcher._consume_kafka(consumer)

    # 队列应该有1条消息
    assert batcher.queue.qsize() == 1
    msg = await batcher.queue.get()
    assert msg.value == b"data"
