from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Dict

from smartutils.config.schema.redis import RedisConf
from smartutils.infra.cache.bitmap import RedisBitmap
from smartutils.infra.cache.q_list import SafeQueueList
from smartutils.infra.cache.q_stream import SafeQueueStream
from smartutils.infra.cache.q_zset import SafeQueueZSet
from smartutils.infra.cache.string import SafeString
from smartutils.infra.resource.abstract import AbstractAsyncResource
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger

try:
    from redis.asyncio import ConnectionPool, Redis
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import ConnectionPool, Redis


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
        self.safe_q_stream: SafeQueueStream = SafeQueueStream(self._redis)

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
