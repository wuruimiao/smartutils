from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Optional

from smartutils.infra.cache.const import LuaName
from smartutils.infra.cache.lua_manager import LuaManager
from smartutils.time import get_now_stamp

try:
    from redis.asyncio import Redis
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import Redis


class SafeQueueZSet:
    """
    基于 Redis 的“安全任务优先队列”，采用双 zset（有序集合）结构实现。

    - 主队列 queue: 使用 Redis ZSet 存放待处理任务（score 可表示优先级或时间戳）。
    - pending 队列: 使用 Redis ZSet 记录已被领取但尚未完成的任务（score 通常为领取/处理的时间戳）。

    核心用途：实现任务的原子领取（防止丢任务），易于处理超时任务重投和优先级调度。

    方法说明：
    1. fetch_task_ctx: 弹出 queue 中 score 最小的任务，标记到 pending 集合。业务完成后自动 zrem pending。
    2. requeue_task: 任务处理失败/超时等，从 pending 剔除并重新放入 queue，可重新设定优先级(score)。
    """

    def __init__(self, redis_cli: Redis):
        self._redis: Redis = redis_cli

    @asynccontextmanager
    async def fetch_task_ctx(
        self, queue: str, pending: str, priority: Optional[int] = None
    ) -> AsyncGenerator[Optional[str]]:
        """
        原子领取任务。弹出 queue(zset) 中优先级最高（score 最小）的任务，放入 pending(zset) 并记录当前时间/优先级，
        用于保证任务领取-处理中原子操作。

        场景：分布式任务调度、优先级队列/超时重试恢复、可靠任务分发等。

        :param queue: 主队列 zset key，存待处理任务（已按分数排序）
        :param pending: 待确认队列 zset key，存已被消费者领取、未完结任务
        :param priority: 本次领取任务的 priority/时间戳（zset的分数），可自定义，默认当前时间
        :yields: 任务内容（字符串），若无任务则为 None
        用法建议：
        ```
        async with safe_queue.fetch_task_ctx(queue, pending) as task:
            if task:
                ...  # 处理任务
        ```
        """
        if not priority:
            priority = get_now_stamp()
        # 取分数最小的任务，转移到processing

        msg = await LuaManager.call(
            LuaName.ZPOPMIN_ZADD,
            self._redis,
            keys=[queue, pending],
            args=[priority],
        )
        if msg:
            yield msg
            await self._redis.zrem(pending, msg)
            return
        yield None

    async def requeue_task(
        self, queue: str, pending: str, task: str, score: int
    ) -> str:
        """
        任务回队（重试）。从 pending(zset) 移除某个 task，并将其带指定优先级/分数放回主队列 queue(zset)。

        场景：处理失败、超时重试、人工回滚等。

        :param queue: 主队列 zset key
        :param pending: 待确认队列 zset key
        :param task: 需回队的任务内容或唯一标识
        :param score: 回队后分数（优先级/下次调度时间戳等）
        :return: 实际被回归队列的 task 内容
        """
        return await LuaManager.call(
            LuaName.ZREM_ZADD,
            self._redis,
            keys=[queue, pending],
            args=[task, score],
        )
