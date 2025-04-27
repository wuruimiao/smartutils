import pytest
import asyncio
import json
import time

TEST_TOPIC = "pytest-test-topic"
GROUP_ID = "pytest-group"


@pytest.fixture(scope="session", autouse=True)
async def setup_kafka(tmp_path_factory):
    config_str = """
kafka:
  bootstrap_servers:
    - host: 192.168.1.56
      port: 19092
  client_id: unmanned
  acks: all
  compression_type: zstd
  max_batch_size: 16384
  linger_ms: 0
  request_timeout_ms: 1000
  retry_backoff_ms: 100"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    from smartutils.config import init
    init(str(config_file))
    print(config_file)

    from smartutils.mq import init
    init()
    from smartutils.mq import kafka_service

    await kafka_service.start_producer()
    yield
    await kafka_service.close()


@pytest.mark.asyncio
async def test_send_and_consume():
    from smartutils.mq import kafka_service
    import uuid

    data = [{"msg": "hello"}, {"msg": "world"}]
    await kafka_service.send_data(TEST_TOPIC, data)
    await asyncio.sleep(1)

    group_id = f"pytest-group-{uuid.uuid4()}"
    consumer = kafka_service.consumer(TEST_TOPIC, group_id, auto_offset_reset="earliest")
    await consumer.start()
    received = []
    try:
        start = time.time()
        while len(received) < len(data) and time.time() - start < 10:
            try:
                msg = await asyncio.wait_for(consumer.getone(), timeout=2)
                received.append(json.loads(msg.value.decode("utf-8")))
            except asyncio.TimeoutError:
                break
    finally:
        await consumer.stop()

    assert {"msg": "hello"} in received
    assert {"msg": "world"} in received


@pytest.mark.asyncio
async def test_send_and_batch_consume():
    """测试 KafkaBatchConsumer 批量消费"""
    from smartutils.mq import KafkaBatchConsumer, kafka_service

    messages_to_send = [{"msg": f"batch_{i}"} for i in range(3)]
    await kafka_service.send_data(TEST_TOPIC, messages_to_send)
    got = []

    async def process_func(msg_list):
        # msg_list 是 [json_str, ...]
        got.extend(msg_list)

    # 单独给每次 batch 消费用个新 group_id
    consumer = KafkaBatchConsumer(
        process_func,
        topic=TEST_TOPIC,
        group_id=GROUP_ID + "-batch",
        batch_size=2,
        timeout=2
    )

    # 用 asyncio.wait_for 限制总执行时间，避免死等
    try:
        await asyncio.wait_for(consumer.start(), timeout=8)
    except asyncio.TimeoutError:
        pass

    # 校验至少收到3条
    assert any("batch_0" in s for s in got)
    assert any("batch_1" in s for s in got)
    assert any("batch_2" in s for s in got)
