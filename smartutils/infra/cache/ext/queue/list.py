from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import List, Optional

from smartutils.infra.cache.ext.queue.abstract import (
    AbstractSafeQueue,
    Task,
    TaskID,
)
from smartutils.infra.cache.lua.const import LuaName
from smartutils.infra.cache.lua.lua_manager import LuaManager
from smartutils.time import get_now_stamp


class SafeQueueList(AbstractSafeQueue):
    """
    基于 Redis 的安全任务队列(list+zset)。适用于先进先出（FIFO）任务队列，
    实现可靠弹出、挂起、回队等业务场景。
    - 主队列使用 Redis List 存储待处理任务。
    - 正在处理（pending）任务用 Redis ZSet 暂存，以便可靠性、超时重试等。
    1. fetch_task_ctx: 从 ready list 弹出任务, 放入 pending zset(带时间戳), 业务处理后自动从pending移除。
    2. requeue_task: 任务处理失败/需重入时，将pending任务移回ready list。
    """

    async def task_num(self, queue: str) -> int:
        """
        获取任务队列长度。
        :param queue: 任务队列list名
        :return: int, 任务数量
        """
        return await self._redis.llen(queue)  # type: ignore

    async def enqueue_task(self, queue: str, tasks: List[Task]) -> bool:
        """
        向任务队列尾部添加任务。
        :param queue: 任务队列list名
        :param task: 任务内容(str)
        :return: bool, 是否成功
        """
        _tasks = [t.ID for t in tasks]
        return await self._redis.lpush(queue, *_tasks) > 0  # type: ignore

    async def is_task_pending(self, pending: str, task: TaskID) -> bool:
        """
        检查任务是否在pending队列中。
        :param pending: 处理中任务zset名
        :param task: 任务内容(str)
        :return: bool, 任务是否在pending中
        """
        score = await self._redis.zscore(pending, task)
        return score is not None

    @asynccontextmanager
    async def fetch_task_ctx(
        self, queue: str, pending: str
    ) -> AsyncGenerator[Optional[TaskID]]:
        """
        原子领取任务：从 queue (list) 弹出任务，并放入 pending (zset)，
        适用于work队列的可靠消费。
        - 业务方用 with 语句包裹抢占的任务。
        - 退出上下文时，自动 zrem (归还/完成任务)。
        :param queue: 主任务队列list名
        :param pending: 处理中任务zset名
        :yields: TaskID|None, 本次弹出的任务字符串
        """
        msg = await LuaManager.call(
            LuaName.RPOP_ZADD,
            self._redis,
            keys=[queue, pending],
            args=[get_now_stamp()],
        )
        if msg:
            yield self._decode_bytes.post(msg)  # type: ignore
            await self._redis.zrem(pending, msg)
            return
        yield None

    async def requeue_task(
        self, queue: str, pending: str, task: TaskID, priority=None
    ) -> bool:
        """
        回队任务：将pending(zset)中的task移除，并重新放入queue(list)。
        支持执行失败自动重试/超时重投等场景。
        :param queue: 主任务队列list名
        :param pending: 处理中任务zset名
        :param task: 需归队的任务内容(str)
        :param priority: 兼容时间戳(未使用)，默认最高优先级
        :return: bool, 是否成功
        """
        await LuaManager.call(
            LuaName.ZREM_RPUSH, self._redis, keys=[pending, queue], args=[task]
        )
        return True
