import functools
import logging
import traceback
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Callable, Awaitable, Any
from typing import Optional

import redis.asyncio as redis
from redis.exceptions import ResponseError

from smartutils.config import config
from smartutils.time import get_now_stamp

logger = logging.getLogger(__name__)


class AsyncRedisCli:
    """异步 Redis 客户端封装"""

    def __init__(self):
        redis_conf = config.redis
        self._pool = redis.ConnectionPool.from_url(
            f"redis://{redis_conf['host']}:{redis_conf['port']}",
            password=redis_conf['password'],
            db=redis_conf['db'],
            decode_responses=True,
            max_connections=10
        )
        self._redis = redis.Redis.from_pool(connection_pool=self._pool)

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置键值对，可选过期时间"""
        return await self._redis.set(key, value, ex=expire)

    async def incr(self, key: str, expire: Optional[int] = None) -> str:
        """原子自增计数器
        :param key: Redis键名
        :param expire: 可选过期时间(秒)
        """
        lua_script = '''
        local current = redis.call('incr', KEYS[1])
        if ARGV[1] ~= '' then
            redis.call('expire', KEYS[1], ARGV[1])
        end
        return current
        '''
        return await self._redis.eval(
            lua_script,
            1,
            key,
            str(expire) if expire else ''
        )

    async def decr(self, key: str, expire: Optional[int] = None) -> str:
        """原子自减计数器
        :param key: Redis键名
        :param expire: 可选过期时间(秒)
        """
        lua_script = '''
        local current = redis.call('decr', KEYS[1])
        if ARGV[1] ~= '' then
            redis.call('expire', KEYS[1], ARGV[1])
        end
        return current
        '''
        return await self._redis.eval(
            lua_script,
            1,
            key,
            str(expire) if expire else ''
        )

    async def get(self, key: str) -> Optional[str]:
        """获取键的值"""
        return await self._redis.get(key)

    async def llen(self, key: str) -> int:
        return await self._redis.llen(key)

    async def lpush(self, key: str, *values):
        return await self._redis.lpush(key, *values)

    @asynccontextmanager
    async def safe_rpop_zadd(self, list_key: str, zset_key: str, timestamp: int = None):
        if not timestamp:
            timestamp = get_now_stamp()
        lua_script = """
        local msg = redis.call('rpop', KEYS[1])
        if msg then
            redis.call('zadd', KEYS[2], ARGV[1], msg)
        end
        return msg
        """
        lua = self._redis.register_script(lua_script)
        msg = await lua(keys=[list_key, zset_key], args=[timestamp])
        if msg:
            yield msg
            await self.zrem(zset_key, msg)
            return
        yield None

    async def safe_rpush_zrem(self, list_key: str, zset_key: str, value):
        """
        从zset中删除value，并将该value推入list的右端
        :param list_key:
        :param zset_key:
        :param value:
        :return:
        """
        lua_script = """
        redis.call('ZREM', KEYS[1], ARGV[1])
        redis.call('RPUSH', KEYS[2], ARGV[1])
        return ARGV[1]
        """
        lua = self._redis.register_script(lua_script)
        return await lua(keys=[zset_key, list_key], args=[value])

    async def sadd(self, key, *values):
        await self._redis.sadd(key, *values)

    async def srem(self, key, *values):
        await self._redis.srem(key, *values)

    async def scard(self, key) -> int:
        return await self._redis.scard(key)

    async def xadd(self, stream: str, fields: dict) -> str:
        """添加条目到 Redis Stream"""
        return await self._redis.xadd(stream, fields)

    async def zadd(self, zset_name: str, key: str, score: int) -> bool:
        return await self._redis.zadd(zset_name, {key: score})

    async def zrangebyscore(self, zset_name: str, score_min: int, score_max: int, with_scores: bool = False):
        return await self._redis.zrangebyscore(zset_name, min=score_min, max=score_max, withscores=with_scores)

    async def zrem(self, zset_name: str, *members):
        return await self._redis.zrem(zset_name, *members)

    async def xack(self, stream: str, group: str, message_id: str) -> None:
        """提交 ACK，确认该消息已被处理"""
        await self._redis.xack(stream, group, message_id)

    async def ensure_stream_and_group(self, stream_name: str, group_name: str):
        try:
            await self._redis.xgroup_create(stream_name, group_name, id='0', mkstream=True)
        except ResponseError as e:
            if "BUSYGROUP Consumer Group name already exists" not in str(e):
                raise

    @asynccontextmanager
    async def xread_xack(self, stream: str, group: str, count: int = 1):
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
                block=1000
            )
            if len(messages) > count:
                logger.error(f'xread_xack get {len(messages)} expect {count}')
            # print('messages================', messages)
            if not messages:
                yield None
                return
            logger.info(f'{messages}')
            for message in messages:
                stream_name, messages_list = message
                for message_id, fields in messages_list:
                    message_ids.add(message_id)

                    fields = {key.decode() if isinstance(key, bytes) else key:
                                  value.decode() if isinstance(value, bytes) else value for key, value in
                              fields.items()}
                    yield fields
        except Exception as e:
            logger.error(f"xread xack {traceback.format_exc()} {e}")
            yield None
        finally:
            # 在退出时提交 ACK
            for message_id in message_ids:
                await self._redis.xack(stream, group, message_id)

    async def close(self):
        """关闭 Redis 连接（解绑订阅 & 关闭连接池）"""
        await self._redis.close()
        await self._pool.disconnect()


class Cache:
    def __init__(self):
        self._cache_var = ContextVar(f'cache')
        self._redis_cli = AsyncRedisCli()

    def with_cache(self, func: Callable[..., Awaitable[Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            token = self._cache_var.set(self._redis_cli)
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                raise e
            finally:
                self._cache_var.reset(token)

        return wrapper

    def curr_cache(self) -> AsyncRedisCli:
        try:
            return self._cache_var.get()
        except LookupError as e:
            logger.error(f'curr cache err: {e}')

    async def close(self):
        await self._redis_cli.close()


cache = None


def init():
    global cache
    cache = Cache()
