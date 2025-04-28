import asyncio
import json
import logging
import traceback
from contextlib import asynccontextmanager
from typing import List, Dict, Callable, Optional, Any, AsyncContextManager

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer, TopicPartition, errors

from smartutils.config.schema.kafka import KafkaConf
from smartutils.infra.abstract import AbstractResource

logger = logging.getLogger(__name__)


class AsyncKafkaCli(AbstractResource):
    def __init__(self, conf: KafkaConf, name: str):
        self._conf = conf
        self._name = name
        self._bootstrap_servers = self._conf.urls
        self._producer: Optional[AIOKafkaProducer] = None
        self._producer_lock = asyncio.Lock()

    async def ping(self) -> bool:
        try:
            await self.start_producer()
            await self._producer.client.fetch_all_metadata()
            return True
        except Exception as e:
            logger.warning(f"[{self._name}] Kafka ping failed: {e}")
            return False

    async def close(self):
        if self._producer:
            await self._producer.stop()

    @asynccontextmanager
    async def session(self) -> AsyncContextManager:
        await self.start_producer()
        yield self

    async def _start_producer(self):
        producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers, **self._conf.kw)
        try:
            await producer.start()
            self._producer = producer
        except errors.KafkaConnectionError as e:
            logger.error(f'start kafka producer {self._bootstrap_servers} fail, err: {traceback.format_exc()}')
            await producer.stop()
            raise e

    async def start_producer(self):
        if self._producer:
            return
        async with self._producer_lock:
            if self._producer:
                return
            await self._start_producer()

    def consumer(self, topic: str, group_id: str, auto_offset_reset: str = 'latest'):
        return AIOKafkaConsumer(
            topic,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            bootstrap_servers=self._bootstrap_servers,
            enable_auto_commit=False,
        )

    async def send_data(self, topic: str, data: List[Dict]):
        await self.start_producer()
        for record in data:
            await self._producer.send_and_wait(topic, json.dumps(record).encode('utf-8'))


class KafkaBatchConsumer:
    def __init__(
            self,
            kafka_cli: AsyncKafkaCli,
            process_func: Callable[[List[str]], Any],
            topic: str,
            group_id: str,
            batch_size: int = 10000,
            timeout: int = 1,
    ):
        self.kafka_cli = kafka_cli
        self.topic = topic
        self.group_id = group_id
        self.batch_size = batch_size
        self.timeout = timeout
        self.process_func = process_func
        self.queue = asyncio.Queue(self.batch_size)

    async def start(self):
        consumer: AIOKafkaConsumer = self.kafka_cli.consumer(self.topic, self.group_id, auto_offset_reset='earliest')
        await asyncio.gather(
            self._consume_kafka(consumer),
            self._process_batch(consumer)
        )

    async def _consume_kafka(self, consumer: AIOKafkaConsumer):
        await consumer.start()
        try:
            async for msg in consumer:
                await self.queue.put(msg)
        finally:
            await consumer.stop()

    async def _process_batch(self, consumer: AIOKafkaConsumer):
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
                logger.error(f"batch consume err: {traceback.format_exc()}")
