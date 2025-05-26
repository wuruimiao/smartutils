from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Optional
from smartutils.log import logger

try:
    from redis import asyncio as redis, ResponseError
except ImportError:
    logger.debug("smartutils.infra.cache.cli depend on redis, install before use")
    redis = None
    ResponseError = None


from smartutils.config.schema.redis import RedisConf
from smartutils.error.factory import ExcDetailFactory
from smartutils.error.sys import CacheError
from smartutils.infra.source_manager.abstract import AbstractResource
from smartutils.time import get_now_stamp

__all__ = ["AsyncRedisCli"]


class AsyncRedisCli(AbstractResource):
    """异步 Redis 客户端封装，线程安全、协程安全"""

    def __init__(self, conf: RedisConf, name: str):
        self._name = name

        kw = conf.kw
        kw["decode_responses"] = True
        self._pool = redis.ConnectionPool.from_url(conf.url, **kw)
        self._redis = redis.Redis.from_pool(connection_pool=self._pool)

    async def ping(self) -> bool:
        try:
            pong = await self._redis.ping()
            return pong is True
        except:  # noqa
            logger.exception("Redis health check {name} failed", name=self._name)
            return False

    async def close(self):
        await self._redis.aclose()
        await self._pool.disconnect()

    @asynccontextmanager
    async def session(self):
        yield self

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置键值对，可选过期时间
        :return: 操作是否成功，True/False
        """
        return await self._redis.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        """
        获取键的值。
        :return: 字符串值或 None
        """
        return await self._redis.get(key)

    async def delete(self, *key: str) -> int:
        """
        删除一个或多个键。
        :return: 实际被删除的key数量，int
        """
        return await self._redis.delete(*key)

    async def incr(self, key: str, expire: Optional[int] = None) -> str:
        """
        原子自增计数器。
        :return: 自增后的数值（字符串类型）
        """
        lua_script = """
        local current = redis.call('incr', KEYS[1])
        if ARGV[1] ~= '' then
            redis.call('expire', KEYS[1], ARGV[1])
        end
        return current
        """
        return await self._redis.eval(lua_script, 1, key, str(expire) if expire else "")

    async def decr(self, key: str, expire: Optional[int] = None) -> str:
        """
        原子自减计数器。
        :return: 自减后的数值（字符串类型）
        """
        lua_script = """
        local current = redis.call('decr', KEYS[1])
        if ARGV[1] ~= '' then
            redis.call('expire', KEYS[1], ARGV[1])
        end
        return current
        """
        return await self._redis.eval(lua_script, 1, key, str(expire) if expire else "")

    # 集合
    async def sadd(self, key, *values) -> int:
        """
        向集合添加元素。
        :return: 实际添加的新元素数量，int
        """
        return await self._redis.sadd(key, *values)

    async def srem(self, key, *values) -> int:
        """
        从集合中移除元素。
        :return: 实际移除的元素数量，int
        """
        return await self._redis.srem(key, *values)

    async def scard(self, key: str) -> int:
        """
        获取集合的元素数量。
        :return: 集合大小，int
        """
        return await self._redis.scard(key)

    # list
    async def llen(self, key: str) -> int:
        """
        获取列表长度。
        :return: 列表长度，int
        """
        return await self._redis.llen(key)

    async def rpush(self, key: str, *value: str) -> int:
        """
        从右侧插入一个或多个元素到列表。
        :return: 操作后列表长度，int
        """
        return await self._redis.rpush(key, *value)

    async def lrange(self, key: str, start: int, end: int) -> list:
        """
        获取列表指定区间元素。
        :return: 区间内的元素列表
        """
        return await self._redis.lrange(key, start, end)

    # zset
    async def zadd(self, zset_name: str, key: str, score: int) -> int:
        """
        向有序集合添加一个成员。
        :return: 添加的新成员数量，int
        """
        return await self._redis.zadd(zset_name, {key: score})

    async def zadd_multi(self, zset_name: str, key_score: dict) -> int:
        """
        批量向有序集合添加成员。
        :return: 添加的新成员数量，int
        """
        return await self._redis.zadd(zset_name, key_score)

    async def zcard(self, zset_name) -> int:
        return await self._redis.zcard(zset_name)

    async def zrange(
            self, zset_name: str, start: int, end: int, withscores: bool = False
    ) -> list:
        """
        获取有序集合指定区间成员。
        :return: 成员列表，如 withscores=True 则为[(member, score), ...]
        """
        return await self._redis.zrange(zset_name, start, end, withscores=withscores)

    async def zrangebyscore(
            self, zset_name: str, score_min: int, score_max: int, withscores: bool = False
    ) -> list:
        """
        按分数区间获取有序集合成员。
        :return: 成员列表，如 withscores=True 则为[(member, score), ...]
        """
        return await self._redis.zrangebyscore(
            zset_name, min=score_min, max=score_max, withscores=withscores
        )

    async def zrem(self, zset_name: str, *members: str) -> int:
        """
        删除有序集合中的成员。
        :return: 实际删除的成员数量，int
        """
        return await self._redis.zrem(zset_name, *members)

    # 队列: list
    @asynccontextmanager
    async def safe_rpop_zadd(
            self, list_ready: str, zset_pending: str, score: int = None
    ) -> AsyncGenerator[Optional[str]]:
        """
        安全地从队列弹出任务并放入有序集合。
        :return: 弹出的任务（字符串），若无任务则为None。退出时会自动从有序集合删除该任务。
        """
        """
        获取任务
        """
        if not score:
            score = get_now_stamp()
        lua_script = """
        local msg = redis.call('rpop', KEYS[1])
        if msg then
            redis.call('zadd', KEYS[2], ARGV[1], msg)
        end
        return msg
        """
        lua = self._redis.register_script(lua_script)
        msg = await lua(keys=[list_ready, zset_pending], args=[score])
        if msg:
            yield msg
            await self.zrem(zset_pending, msg)
            return
        yield None

    async def safe_rpush_zrem(
            self, list_ready: str, zset_pending: str, value: str
    ) -> str:
        """
        将某任务从有序集合移除并放回队列。
        :return: 被重新放回队列的元素值（字符串）
        """
        lua_script = """
        redis.call('ZREM', KEYS[1], ARGV[1])
        redis.call('RPUSH', KEYS[2], ARGV[1])
        return ARGV[1]
        """
        lua = self._redis.register_script(lua_script)
        return await lua(keys=[zset_pending, list_ready], args=[value])

    # 队列：zset
    @asynccontextmanager
    async def safe_zpop_zadd(
            self, zset_ready: str, zset_pending: str, score: int = None
    ) -> AsyncGenerator[Optional[str]]:
        """
        安全地从有序集合弹出优先级最高任务并放入另一有序集合。
        :return: 弹出的任务（字符串），若无则为None。退出时自动从pending集合删除该任务。
        """
        if not score:
            score = get_now_stamp()
        # 取分数最小的任务，转移到processing
        lua_script = """
        local items = redis.call('zpopmin', KEYS[1], 1)
        if items and #items > 0 then
            redis.call('zadd', KEYS[2], ARGV[1], items[1])
            return items[1]
        end
        return nil
        """
        lua = self._redis.register_script(lua_script)
        msg = await lua(keys=[zset_ready, zset_pending], args=[score])
        if msg:
            yield msg
            await self.zrem(zset_pending, msg)
            return
        yield None

    async def safe_zrem_zadd(
            self, zset_processing: str, zset_ready: str, value: str, score: int
    ) -> str:
        """
        从处理中集合移除任务并归还到等待队列（可调整优先级）。
        :return: 归还到队列的元素值（字符串）
        """
        lua_script = """
        redis.call('zrem', KEYS[1], ARGV[1])
        redis.call('zadd', KEYS[2], ARGV[2], ARGV[1])
        return ARGV[1]
        """
        lua = self._redis.register_script(lua_script)
        return await lua(keys=[zset_processing, zset_ready], args=[value, score])

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
                    "xread_xack get {length} expect {count}",
                    length=len(messages),
                    count=count,
                )
            # print('messages================', messages)
            if not messages:
                yield None
                return
            logger.debug("{messages}", messages=messages)
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
            logger.exception(f"xread xack fail")
            yield None
        finally:
            # 在退出时提交 ACK
            for message_id in message_ids:
                await self._redis.xack(stream, group, message_id)
