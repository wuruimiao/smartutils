from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Dict, Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.redis import RedisConf
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import singleton
from smartutils.error.factory import ExcDetailFactory
from smartutils.error.sys import CacheError
from smartutils.infra.source_manager.abstract import AbstractResource
from smartutils.infra.source_manager.manager import CTXResourceManager
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger
from smartutils.time import get_now_stamp

try:
    from redis.asyncio import ConnectionPool, Redis, ResponseError
except ImportError:
    pass
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import ConnectionPool, Redis, ResponseError

__all__ = ["AsyncRedisCli", "RedisManager"]


class AsyncRedisCli(LibraryCheckMixin, AbstractResource):
    """异步 Redis 客户端封装，线程安全、协程安全。"""

    def __init__(self, conf: RedisConf, name: str):
        self.check(conf=conf, libs=["redis"])

        self._key = name

        kw = conf.kw
        kw["decode_responses"] = True
        self._pool: ConnectionPool = ConnectionPool.from_url(conf.url, **kw)
        self._redis: Redis = Redis.from_pool(connection_pool=self._pool)

    def __getattr__(self, name):
        # 当访问 AsyncRedisCli 未定义的属性/方法时，由 _redis 处理
        return getattr(self._redis, name)

    async def ping(self) -> bool:
        try:
            pong = await self._redis.ping()
            return pong is True
        except:  # noqa
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
        return await self._redis.eval(*args, **kwargs)  # type: ignore

    async def incr(self, key: str, ex: Optional[int] = None) -> str:
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
        return await self._eval(lua_script, 1, key, str(ex) if ex else "")

    async def decr(self, key: str, ex: Optional[int] = None) -> str:
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
        return await self._eval(lua_script, 1, key, str(ex) if ex else "")

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

    # 队列: list
    @asynccontextmanager
    async def safe_rpop_zadd(
        self, list_ready: str, zset_pending: str, score: Optional[int] = None
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
        self, zset_ready: str, zset_pending: str, score: Optional[int] = None
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


@singleton
@CTXVarManager.register(CTXKey.CACHE_REDIS)
class RedisManager(LibraryCheckMixin, CTXResourceManager[AsyncRedisCli]):
    """
    Redis 常用命令返回值内容与类型总结（根据 tests_real/test_redis_ret_type.py 验证）：

    - 字符串/数值类：
        set/setex/psetex            -> bool          # 操作是否成功
        get/getset/getdel           -> str/None      # 字符串结果，不存在为None
        incr/incrby/decr/decrby     -> int/str       # 自增/自减后结果（通常int，部分兼容str for lua脚本场景）
        mset                        -> bool          # 操作是否成功
        mget                        -> List[str]     # 多个key的结果，没有的为None
        msetnx                      -> bool          # 表示所有都设置成功

    - set 集合相关：
        sadd/srem                   -> int           # 实际变动元素数
        scard                       -> int           # 元素数量

    - list 列表相关：
        llen/rpush/lpush            -> int           # 列表长度
        lrange                      -> List[str]     # 区间元素

    - zset 有序集合：
        zadd/zrem                   -> int           # 新增/删除数
        zcard                       -> int           # 数量
        zrange/zrangebyscore        -> List[str]     # 区间成员
        zrange(withscores=True)     -> List[Tuple[str, float]]

    - hash 字典相关：
        hset/hdel                   -> int           # 变更数
        hget                        -> str/None      # Value
        hgetall                     -> dict[str, str]# 所有字段

    - key 相关:
        delete                      -> int           # 删除key数
        exists                      -> int           # 存在key数
        expire/ttl/persist/touch    -> int/bool      # 是否成功/剩余时长/被修改key数
        type                        -> str           # 存储结构类型
        randomkey                   -> str/None      # 任意key
        scan                        -> Tuple[int | str, List[str]]    # 游标和key

    - stream 相关：
        xadd                        -> str           # 流ID
        xreadgroup/xread            -> List          # 消息对象
        xack                        -> int           # ack 成功条数

    - 脚本：
        eval/evalsha/script_load    -> 任意           # 依赖返回的lua脚本
        script_exists               -> List[bool]    # 存在性判断
        script_flush                -> None/str      # 无

    - 其它杂项及管理：
        rename/move/restore/copy    -> bool          # 是否成功
        dump                        -> bytes/None    # 序列化值
        publish                     -> int           # 订阅接收数
        pfadd/pfcount/pfmerge       -> int           # HyperLogLog 使用
        sort                        -> List[str]     # 排序结果
        slowlog_get                 -> List          # 慢日志
        slowlog_len                 -> int           # 长度
        memory_stats                -> dict          # 内存信息
        memory_usage                -> int/None      # 占用字节
        wait/save/flushall          -> int/str       # 保存/刷新响应
        info                        -> dict          # 服务器信息
        bit相关(setbit,getbit,etc)  -> int           # 位值/计数

    均通过实际用例和断言验证。
    如需新的命令类型、内容总结，请查阅redis文档或相关测试用例。
    """

    def __init__(self, confs: Optional[Dict[str, RedisConf]] = None):
        self.check(conf=confs)
        assert confs

        resources = {k: AsyncRedisCli(conf, f"redis_{k}") for k, conf in confs.items()}
        super().__init__(
            resources=resources,
            ctx_key=CTXKey.CACHE_REDIS,
            error=CacheError,
        )

    @property
    def curr(self) -> AsyncRedisCli:
        return super().curr


@InitByConfFactory.register(ConfKey.REDIS)
def _(conf):
    RedisManager(conf)
