import json
import traceback
from typing import List, Dict, Callable, Optional
from smartutils.config import config
import asyncio
import logging

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer, TopicPartition, errors

logger = logging.getLogger(__name__)


class KafkaService:
    def __init__(self):
        self._conf = config.kafka
        self._bootstrap_servers = self._conf.urls
        self._producer: Optional[AIOKafkaProducer] = None

    async def start_producer(self):
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers, **self._conf.kw)
        try:
            await self._producer.start()
        except errors.KafkaConnectionError as e:
            logger.error(f'start kafka producer {self._bootstrap_servers} fail, err: {traceback.format_exc()}')

    def consumer(self, topic: str, group_id: str, auto_offset_reset: str = 'latest'):
        return AIOKafkaConsumer(
            topic,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            bootstrap_servers=self._bootstrap_servers,
            enable_auto_commit=False,
        )

    async def close(self):
        await self._producer.stop()

    async def send_data(self, topic: str, data: List[Dict]):
        for record in data:
            await self._producer.send_and_wait(topic, json.dumps(record).encode('utf-8'))


kafka_service: Optional[KafkaService] = None


async def init():
    global kafka_service
    kafka_service = KafkaService()
    await kafka_service.start_producer()


class KafkaBatchConsumer:
    def __init__(self, process_func: Callable, topic: str, group_id: str, batch_size: int = 10000, timeout: int = 1):
        """
        通用 Kafka 批量消费者
        :param topic: 监听的 Topic
        :param group_id: 消费者组 ID
        :param batch_size: 触发批量处理的消息数
        :param timeout: 超时时间（秒），即使未达到 batch_size 也会触发处理
        :param process_func: 处理数据的异步函数，接受 List[str]（消息 JSON 列表）
        """
        self.topic = topic
        self.group_id = group_id
        self.batch_size = batch_size
        self.timeout = timeout
        self.process_func = process_func
        self.queue = asyncio.Queue(self.batch_size)  # 内部缓冲队列

    async def start(self):
        """
        启动 Kafka 消费者和批量处理任务
        """
        consumer: AIOKafkaConsumer = kafka_service.consumer(self.topic, self.group_id, auto_offset_reset='earliest')
        await asyncio.gather(
            self._consume_kafka(consumer),
            self._process_batch(consumer)
        )

    async def _consume_kafka(self, consumer: AIOKafkaConsumer):
        """
        Kafka 消费者，监听单个 Topic，手动提交 Offset
        """
        await consumer.start()
        try:
            async for msg in consumer:
                await self.queue.put(msg)
        finally:
            await consumer.stop()

    async def _process_batch(self, consumer: AIOKafkaConsumer):
        """
        批量处理 Kafka 消息，手动提交 Offset
        """
        while True:
            batch = []
            try:
                msg = await self.queue.get()
                batch.append(msg)

                while len(batch) < self.batch_size:
                    try:
                        msg = await asyncio.wait_for(self.queue.get(), timeout=self.timeout)
                        batch.append(msg)
                    except asyncio.TimeoutError:
                        break

                messages = [msg.value.decode('utf-8') for msg in batch]
                await self.process_func(messages)
                if batch:
                    partition_offsets = {}
                    for msg in batch:
                        tp = TopicPartition(msg.topic, msg.partition)
                        current = partition_offsets.get(tp, -1)
                        if msg.offset > current:
                            partition_offsets[tp] = msg.offset

                    commit_offsets = {tp: o + 1 for tp, o in partition_offsets.items()}
                    await consumer.commit(commit_offsets)

            except Exception as e:
                logger.error(f"批量处理出错: {e} {traceback.format_exc()}")
