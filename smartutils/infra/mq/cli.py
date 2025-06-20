from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Dict, List, Optional

import orjson

from smartutils.config.schema.kafka import KafkaConf
from smartutils.error.factory import ExcDetailFactory
from smartutils.error.sys import MQError
from smartutils.infra.source_manager.abstract import AbstractResource
from smartutils.log import logger

try:
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, TopicPartition, errors
except ImportError:
    pass
if TYPE_CHECKING:
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, TopicPartition, errors

__all__ = ["AsyncKafkaCli", "KafkaBatchConsumer"]


msg = "smartutils.infra.mq.cli depend on aiokafka, install before use"


class AsyncKafkaCli(AbstractResource):
    def __init__(self, conf: KafkaConf, name: str):
        assert AIOKafkaProducer, msg

        self._conf = conf
        self._name = name
        self._bootstrap_servers = self._conf.urls
        self._producer: Optional[AIOKafkaProducer] = None
        self._producer_lock = asyncio.Lock()

    async def ping(self) -> bool:
        try:
            await self.start_producer()
            assert self._producer, "AsyncKafkaCli start producer failed."
            await self._producer.client.fetch_all_metadata()
            return True
        except Exception as e:
            logger.warning("[{name}] Kafka ping failed: {e}", name=self._name, e=e)
            return False

    async def close(self):
        if self._producer:
            await self._producer.stop()

    @asynccontextmanager
    async def db(
        self, use_transaction: bool = True
    ) -> AsyncGenerator["AsyncKafkaCli", None]:
        await self.start_producer()
        yield self

    async def _start_producer(self):
        producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers, **self._conf.kw
        )
        try:
            await producer.start()
            self._producer = producer
        except errors.KafkaConnectionError as e:
            logger.exception(
                "start kafka producer {servers} fail", servers=self._bootstrap_servers
            )
            await producer.stop()
            raise MQError(ExcDetailFactory.get(e)) from None

    async def start_producer(self):
        if self._producer:
            return
        async with self._producer_lock:
            if self._producer:
                return
            await self._start_producer()

    def consumer(self, topic: str, group_id: str, auto_offset_reset: str = "latest"):
        return AIOKafkaConsumer(
            topic,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            bootstrap_servers=self._bootstrap_servers,
            enable_auto_commit=False,
        )

    async def send_data(self, topic: str, data: List[Dict]):
        await self.start_producer()
        assert self._producer, "AsyncKafkaCli start producer failed."
        for record in data:
            await self._producer.send_and_wait(topic, orjson.dumps(record))


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
        self._should_stop = asyncio.Event()

    async def start(self):
        consumer: AIOKafkaConsumer = self.kafka_cli.consumer(
            self.topic, self.group_id, auto_offset_reset="earliest"
        )
        await asyncio.gather(
            self._consume_kafka(consumer), self._process_batch(consumer)
        )

    async def stop(self):
        self._should_stop.set()

    async def _consume_kafka(self, consumer):
        await consumer.start()
        try:
            async for msg in consumer:
                await self.queue.put(msg)
        finally:
            await consumer.stop()

    async def _process_batch(self, consumer):
        while not self._should_stop.is_set():
            batch = []
            try:
                msg = await self.queue.get()
                batch.append(msg)
                while len(batch) < self.batch_size:
                    try:
                        msg = await asyncio.wait_for(
                            self.queue.get(), timeout=self.timeout
                        )
                        batch.append(msg)
                    except asyncio.TimeoutError:
                        break

                messages = [msg.value.decode("utf-8") for msg in batch]
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

            except:  # noqa
                logger.exception("batch consume fail.")
