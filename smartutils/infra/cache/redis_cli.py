from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from smartutils.config.schema.redis import RedisConf
from smartutils.design import proxy_wrapper
from smartutils.infra.cache.bitmap import RedisBitmap
from smartutils.infra.cache.decode import DecodeBytes
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

# if Redis is None:

#     class AsyncRedisCli(LibraryCheckMixin):
#         def __init__(self, *args, **kwargs) -> None:
#             self.check(libs=["redis"])
# else:


class AsyncRedisCli(LibraryCheckMixin, AbstractAsyncResource):
    """异步 Redis 客户端封装，线程安全、协程安全。"""

    def __init__(self, conf: RedisConf, name: str):
        self.check(conf=conf, libs=["redis"])

        self._key = name

        kw = conf.kw
        self._decode_bytes = DecodeBytes(conf.decode_responses)
        self._pool: ConnectionPool = ConnectionPool.from_url(conf.url, **kw)
        self._redis: Redis = Redis.from_pool(connection_pool=self._pool)
        # 尝试直接继承Redis，但反而会导致多处常用方法提示报错，如sadd
        # 从from_pool而来
        # super().__init__(connection_pool=self._pool, auto_close_connection_pool=True)

        # 直接传入self，evalsha需要做兼容，否则register_script报错
        # 后续还要考虑新加方法的兼容性
        self.bitmap: RedisBitmap = RedisBitmap(self._redis, self._decode_bytes)
        self.safe_str: SafeString = SafeString(self._redis, self._decode_bytes)
        self.safe_q_list: SafeQueueList = SafeQueueList(self._redis, self._decode_bytes)
        self.safe_q_zset: SafeQueueZSet = SafeQueueZSet(self._redis, self._decode_bytes)
        self.safe_q_stream: SafeQueueStream = SafeQueueStream(
            self._redis, self._decode_bytes
        )

    def __getattr__(self, name):
        # 当访问 AsyncRedisCli 未定义的属性/方法时，由 _redis 处理
        attr = getattr(self._redis, name)
        if not callable(attr):
            return attr
        return proxy_wrapper(
            attr,
            # redis decode_responses开启时，
            # pre仍需要以兼容my_decode_responses，post自定义解码需禁用
            pre=self._decode_bytes.pre,
            post=self._decode_bytes.post,
        )

    async def evalsha(self, sha: str, keys=None, args=None):
        """
        用sha1调用redis脚本。
        aioredlock分布式锁必需：用于适配AsyncRedisCli为aioredlock客户端实例
        redis-py要求 keys, args 分开传, aioredlock是keys/args分开。
        """
        keys = keys or []
        args = args or []
        # redis-py 7.0+: evalsha的签名为 evalsha(sha, numkeys, *keys_and_args)
        # aioredlock使用aioredis，调用方式为 evalsha(sha, keys=[...], args=[...])
        return await self._redis.evalsha(sha, len(keys), *(keys + args))  # type: ignore

    async def ping(self) -> bool:
        try:
            pong = await self._redis.ping()
            return pong is True
        except:  # noqa: E722
            logger.exception("{} {} health check  failed", self.name, self._key)
            return False

    async def close(self):
        await self._redis.aclose()
        await self._pool.disconnect()

    @asynccontextmanager
    async def db(
        self, use_transaction: bool = False
    ) -> AsyncGenerator["AsyncRedisCli", None]:
        yield self
