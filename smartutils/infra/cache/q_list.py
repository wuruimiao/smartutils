from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Optional

from smartutils.infra.cache.const import RPOP_ZADD_SCRIPT, LuaName
from smartutils.infra.cache.lua_manager import LuaManager
from smartutils.time import get_now_stamp

try:
    from redis.asyncio import Redis
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import Redis


class SafeQueueList:
    """
    基于 Redis 的安全任务队列(list+zset)。
    实现可靠弹出、挂起、回队等业务场景。
    - 主队列使用 Redis List 存储待处理任务。
    - 正在处理（pending）任务用 Redis ZSet 暂存，以便可靠性、超时重试等。
    1. claim_task_ctx: 从 ready list 弹出任务, 放入 pending zset(带时间戳), 业务处理后自动从pending移除。
    2. requeue_task: 任务处理失败/需重入时，将pending任务移回ready list。
    """

    def __init__(self, redis_cli: Redis):
        self._redis: Redis = redis_cli

    @asynccontextmanager
    async def fetch_task_ctx(
        self, queue: str, pending: str, priority: Optional[int] = None
    ) -> AsyncGenerator[Optional[str]]:
        """
        原子领取任务：从 queue (list) 弹出任务，并放入 pending (zset)，
        适用于work队列的可靠消费。
        - 业务方用 with 语句包裹抢占的任务。
        - 退出上下文时，自动 zrem (归还/完成任务)。
        :param queue: 主任务队列list名
        :param pending: 处理中任务zset名
        :param priority: 预定时间戳(默认当前时间)
        :yields: str|None, 本次弹出的任务字符串
        """
        if not priority:
            priority = get_now_stamp()

        msg = await LuaManager.call(
            LuaName.RPOP_ZADD, self._redis, keys=[queue, pending], args=[priority]
        )
        if msg:
            yield msg
            await self._redis.zrem(pending, msg)
            return
        yield None

    async def requeue_task(self, queue: str, pending: str, task: str) -> str:
        """
        回队任务：将pending(zset)中的task移除，并重新放入queue(list)。
        支持执行失败自动重试/超时重投等场景。
        :param queue: 主任务队列list名
        :param pending: 处理中任务zset名
        :param task: 需归队的任务内容(str)
        :return: str, 被重新放回队列的元素值
        """
        lua_script = """
        redis.call('ZREM', KEYS[1], ARGV[1])
        redis.call('RPUSH', KEYS[2], ARGV[1])
        return ARGV[1]
        """
        lua = self._redis.register_script(lua_script)
        return await lua(keys=[pending, queue], args=[task])
