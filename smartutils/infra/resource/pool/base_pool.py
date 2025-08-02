import asyncio
import time
from typing import Generic, Optional

from smartutils.error.sys import PoolOverflowError
from smartutils.infra.resource.abstract import AbstractAsyncResourceT
from smartutils.infra.resource.pool.state.abstract import AbstractPoolState
from smartutils.infra.resource.pool.sync.abstract import PoolSync, PoolSyncAsync
from smartutils.server import Context


class SyncPoolBase(Generic[AbstractAsyncResourceT]):
    """
    通用同步对象池, 线程/进程安全。

    示例用法:
        pool = SyncPool(state, sync, creator, closer, max_size)
        obj = pool.acquire(timeout=3)
        pool.release(obj)
    """

    def __init__(
        self,
        state: AbstractPoolState[AbstractAsyncResourceT],
        sync: PoolSync,
    ):
        self._state: AbstractPoolState[AbstractAsyncResourceT] = state
        self._sync: PoolSync = sync
        self._closed = False
        self._sync.start_background_task(self._reaper)

    def _reaper(self):
        """
        池对象定期回收，安全支持各并发环境；由适配器后台线程/协程定期执行。
        """
        while not self._closed:
            with self._sync.lock():
                self._state.reap()
            time.sleep(self._state.pool_recycle)

    def close(self) -> None:
        """
        关闭池，回收所有资源。
        """
        with self._sync.lock():
            self._closed = True
            self._state.close()

    def acquire(self, ctx: Optional[Context] = None) -> AbstractAsyncResourceT:
        """
        获取池对象，阻塞/超时。线程/进程安全。

        参数:
            timeout (float|None): 超时时间，秒。None表示无限等待。
        返回:
            AbstractResourceT: 对象实例
        异常:
            PoolOverflowError: 获取超时
        """
        ctx = ctx or Context(self._state.pool_timeout)
        while True:
            with self._sync.lock():
                obj = self._state.acquire()
            if obj is not None:
                return obj

            if ctx.timeoutd():
                raise PoolOverflowError()

            self._sync.wait(timeout=ctx.remain_sec())

    def release(self, obj: AbstractAsyncResourceT) -> None:
        """
        归还对象到池，自动溢出归还、清理。线程/进程安全。

        参数:
            obj (AbstractResourceT): 待归还对象
        """
        with self._sync.lock():
            self._state.release(obj)
            self._sync.notify()


class AsyncPoolBase(Generic[AbstractAsyncResourceT]):
    """
    通用异步对象池，适用于 asyncio 等协程环境。

    示例用法:
        pool = AsyncPool(state, sync, creator, closer, max_size)
        obj = await pool.acquire(timeout=3)
        await pool.release(obj)
    """

    def __init__(
        self,
        state: AbstractPoolState[AbstractAsyncResourceT],
        sync: PoolSyncAsync,
    ):
        self._state: AbstractPoolState[AbstractAsyncResourceT] = state
        self._sync: PoolSyncAsync = sync
        self._closed = False
        self._sync.start_background_task(self._reaper)

    async def _reaper(self):  # type: ignore
        """
        池对象定期回收，安全支持各并发环境；由适配器后台线程/协程定期执行。
        """
        while not self._closed:
            async with self._sync.lock():
                self._state.reap()
            await asyncio.sleep(self._state.pool_recycle)

    async def close(self) -> None:
        """
        关闭池，回收所有资源。
        """
        async with self._sync.lock():
            self._closed = True
            self._state.close()

    async def acquire(self, ctx: Optional[Context] = None) -> AbstractAsyncResourceT:
        """
        协程异步获取池对象。

        参数:
            timeout (float|None): 超时时间，秒。None表示无限等待。
        返回:
            AbstractResourceT: 对象实例
        异常:
            PoolOverflowError: 超时
        """
        ctx = ctx or Context(self._state.pool_timeout)
        while True:
            async with self._sync.lock():
                obj = self._state.acquire()
            if obj is not None:
                return obj
            if ctx.timeoutd():
                raise PoolOverflowError()

            await self._sync.wait(timeout=ctx.remain_sec())

    async def release(self, obj: AbstractAsyncResourceT) -> None:
        """
        协程异步归还对象。

        参数:
            obj (AbstractResourceT): 待归还对象
        """

        async with self._sync.lock():
            self._state.release(obj)
            await self._sync.notify()
