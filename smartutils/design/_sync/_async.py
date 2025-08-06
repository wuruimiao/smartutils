import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Union

from smartutils.design._sync.abstract import IAsyncLock


class AsyncioSyncLock(IAsyncLock):
    """
    基于 asyncio 的协程环境同步锁实现。
    使用 asyncio.Condition 实现互斥锁、条件等待、唤醒、多协程安全。

    安全说明：
    ---------------
    - 仅适用于 asyncio 事件循环环境。
    - 支持并发多协程安全，适合 async 生产者-消费者、信号量、队列等场景。
    - 所有超时参数 timeout 必须指定，单位为秒，支持 float/int。
    - 不建议与多线程/多进程同步原语混用。
    """

    def __init__(self, timeout: Union[float, int] = 60 * 60 * 1) -> None:
        self._lock = asyncio.Lock()
        self._cond = asyncio.Condition(self._lock)
        self._timeout = timeout

    async def aacquire(self, timeout: Union[float, int]) -> bool:
        """
        异步方式获取锁，支持超时。
        :param timeout: 超时时间（秒），float 或 int。
        :return: 成功返回 True，超时返回 False。
        """
        try:
            await asyncio.wait_for(self._cond.acquire(), timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def arelease(self) -> None:
        """
        异步释放锁，仅限在已持有锁情况下调用。
        """
        self._cond.release()

    async def a_wait(self, timeout: Union[float, int]) -> bool:
        """
        异步条件等待，支持超时。
        :param timeout: 最长等待秒数。
        :return: 被唤醒则 True，超时则 False。
        """
        try:
            await asyncio.wait_for(self._cond.wait(), timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def anotify(self, n: int = 1) -> None:
        """
        唤醒等待队列中的 n 个协程。
        :param n: 唤醒数量。
        """
        self._cond.notify(n)

    async def anotify_all(self) -> None:
        """
        唤醒所有等待队列中的协程。
        """
        self._cond.notify_all()

    @asynccontextmanager
    async def acontext(self) -> AsyncGenerator[None, None]:
        """
        异步上下文管理器，用于 async with。
        自动加锁/解锁。
        """
        await self.aacquire(timeout=self._timeout)
        try:
            yield
        finally:
            await self.arelease()
