from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Dict, Optional

from smartutils.config.schema.redis import RedisConf
from smartutils.error.factory import ExcDetailFactory
from smartutils.error.sys import CacheError
from smartutils.infra.cache.bitmap import RedisBitmap
from smartutils.infra.cache.q_list import SafeQueueList
from smartutils.infra.cache.q_zset import SafeQueueZSet
from smartutils.infra.cache.string import SafeString
from smartutils.infra.resource.abstract import AbstractAsyncResource
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger
from smartutils.time import get_now_stamp

try:
    from redis.asyncio import ConnectionPool, Redis, ResponseError
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import ConnectionPool, Redis, ResponseError


class AsyncRedisCli(LibraryCheckMixin, AbstractAsyncResource):
    """异步 Redis 客户端封装，线程安全、协程安全。"""

    def __init__(self, conf: RedisConf, name: str):
        self.check(conf=conf, libs=["redis"])

        self._key = name

        kw = conf.kw
        kw["decode_responses"] = True
        self._pool: ConnectionPool = ConnectionPool.from_url(conf.url, **kw)
        self._redis: Redis = Redis.from_pool(connection_pool=self._pool)
        self.bitmap: RedisBitmap = RedisBitmap(self._redis)
        self.safe_str: SafeString = SafeString(self._redis)
        self.safe_q_list: SafeQueueList = SafeQueueList(self._redis)
        self.safe_q_zset: SafeQueueZSet = SafeQueueZSet(self._redis)

    def __getattr__(self, name):
        # 当访问 AsyncRedisCli 未定义的属性/方法时，由 _redis 处理
        return getattr(self._redis, name)

    async def evalsha(self, sha: str, keys=None, args=None):
        """
        用sha1调用redis脚本。
        aioredlock分布式锁必需：用于适配AsyncRedisCli为aioredlock客户端实例
        redis-py要求 keys, args 分开传, aioredlock是keys/args分开。
        """
        keys = keys or []
        args = args or []
        # redis-py 7.0+: evalsha的签名为 evalsha(sha, numkeys, *keys_and_args)
        # aioredlock调用方式为 evalsha(sha, keys=[...], args=[...])
        return await self._redis.evalsha(sha, len(keys), *(keys + args))  # type: ignore

    async def ping(self) -> bool:
        try:
            pong = await self._redis.ping()
            return pong is True
        except:  # noqa: E722
            logger.exception(
                "{cls_name} {name} health check  failed",
                cls_name=self.name,
                name=self._key,
            )
            return False

    async def close(self):
        await self._redis.aclose()
        await self._pool.disconnect()

    @asynccontextmanager
    async def db(
        self, use_transaction: bool = False
    ) -> AsyncGenerator["AsyncRedisCli", None]:
        yield self

    async def _eval(self, *args, **kwargs):
        # 键值必须使用KEYS传递,集群分槽需要
        return await self._redis.eval(*args, **kwargs)  # type: ignore

    # zset
    async def zadd(self, zset_name: str, key: str, score: int) -> int:
        """
        向有序集合添加一个成员。
        :return: 添加的新成员数量，int
        """
        return await self._redis.zadd(zset_name, {key: score})

    async def zadd_multi(self, zset_name: str, key_score: Dict[str, int]) -> int:
        """
        批量向有序集合添加成员。
        :return: 添加的新成员数量，int
        """
        return await self._redis.zadd(zset_name, key_score)

    # stream队列
    async def xadd(self, stream: str, fields: dict) -> str:
        """添加条目到 Redis Stream"""
        return await self._redis.xadd(stream, fields)

    async def ensure_stream_and_group(self, stream_name: str, group_name: str):
        try:
            await self._redis.xgroup_create(
                stream_name, group_name, id="0", mkstream=True
            )
        except ResponseError as e:
            if "BUSYGROUP Consumer Group name already exists" not in str(e):
                raise CacheError(ExcDetailFactory.get(e)) from None

    @asynccontextmanager
    async def xread_xack(
        self, stream: str, group: str, count: int = 1
    ) -> AsyncGenerator[Optional[dict], None]:
        """使用 with 语句读取并处理 Redis Stream，自动提交 ACK"""
        message_ids = set()
        try:
            await self.ensure_stream_and_group(stream, group)
            # print('messages================start',)
            # 从 Redis Stream 获取消息
            # TODO: 非阻塞方式有问题
            # messages = await self._redis.xread({stream: "0"}, count=count, block=1000)
            messages = await self._redis.xreadgroup(
                groupname=group,
                consumername="consumer",
                streams={stream: ">"},
                count=count,
                block=1000,
            )
            if len(messages) > count:
                logger.error(
                    "{name} xread_xack get {length} expect {count}",
                    name=self.name,
                    length=len(messages),
                    count=count,
                )
            # print('messages================', messages)
            if not messages:
                yield None
                return
            logger.debug("{name} {messages}", name=self.name, messages=messages)
            for message in messages:
                stream_name, messages_list = message
                for message_id, fields in messages_list:
                    message_ids.add(message_id)

                    fields = {
                        key.decode() if isinstance(key, bytes) else key: (
                            value.decode() if isinstance(value, bytes) else value
                        )
                        for key, value in fields.items()
                    }
                    yield fields
        except:  # noqa
            logger.exception("{name} xread xack fail", name=self.name)
            yield None
        finally:
            # 在退出时提交 ACK
            for message_id in message_ids:
                await self._redis.xack(stream, group, message_id)
