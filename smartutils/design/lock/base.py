import asyncio
import multiprocessing
import sys
import threading
from typing import Optional, Tuple

from smartutils.design.lock.abstract import LockBase
from smartutils.log import logger

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import override
else:  # pragma: no cover
    from typing_extensions import override


def _check(blocking: bool, timeout: Optional[float]) -> Tuple[bool, Optional[float]]:
    """
    校验并标准化 blocking 和 timeout 参数，使其符合语义。
    只会返回：
        - (False, None)：非阻塞，立即返回
        - (True, None)：阻塞，无限等待
        - (True, >0)：阻塞，超时等待
    """
    if not blocking:
        # 非阻塞
        if timeout is not None and timeout > 0:
            logger.warning("Ignore timeout={} since blocking=False.", timeout)
        return False, None

    if timeout is not None and timeout == 0:
        # 切非阻塞
        logger.warning("Set Blocking=False since timeout=0.")
        return False, None

    # 阻塞
    if timeout is not None and timeout < 0:
        # 无限等待：
        # threading需要-1，不接受None，才无限等待，后续判断None不传
        # multiprocessing传None无限等待；但 <=0 非阻塞，这里统一为无限等待
        timeout = None

    # None 或 >0
    return True, timeout


class _SyncBase(LockBase):
    """
    统一封装为异步，但实际内部都是同步操作，谨慎使用
    """

    @override
    async def acquire(
        self, blocking: bool = True, timeout: Optional[float] = None
    ) -> bool:
        """获取锁"""
        blocking, timeout = _check(blocking, timeout)
        if timeout is None:
            # threading不接受None
            return self._lock.acquire(  # pyright: ignore[reportAttributeAccessIssue]
                blocking
            )
        return self._lock.acquire(  # pyright: ignore[reportAttributeAccessIssue]
            blocking, timeout
        )

    @override
    def release(self) -> None:
        """释放锁"""
        self._lock.release()  # pyright: ignore[reportAttributeAccessIssue]

    @override
    async def locked(self) -> bool:
        if hasattr(self._lock, "locked"):  # pyright: ignore[reportAttributeAccessIssue]
            return self._lock.locked()  # pyright: ignore[reportAttributeAccessIssue]
        acquired = self._lock.acquire(  # pyright: ignore[reportAttributeAccessIssue]
            False
        )
        if acquired:
            self._lock.release()  # pyright: ignore[reportAttributeAccessIssue]
            return False
        else:
            return True


class ThreadLock(_SyncBase):
    def __init__(self) -> None:
        self._lock = threading.Lock()


class ProcessLock(_SyncBase):
    def __init__(self) -> None:
        self._lock = multiprocessing.Lock()


class AsyncioLock:
    """
    异步锁，支持 async with
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    async def acquire(
        self, blocking: bool = True, timeout: Optional[float] = None
    ) -> bool:
        """获取异步锁"""
        blocking, timeout = _check(blocking, timeout)

        if blocking and timeout is None:
            # acquire本身无限等待
            return await self._lock.acquire()

        try:
            # wait_for, None无限等待，<=0立即返回，>0等待指定秒数
            await asyncio.wait_for(
                self._lock.acquire(), 0 if timeout is None else timeout
            )
            return True
        except asyncio.TimeoutError:
            return False

    def release(self) -> None:
        """释放锁"""
        self._lock.release()

    def locked(self) -> bool:
        return self._lock.locked()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()
