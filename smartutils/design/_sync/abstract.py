from __future__ import annotations

from typing import Any, AsyncContextManager, Protocol, Union, runtime_checkable


@runtime_checkable
class ISyncLock(Protocol):
    """
    方法说明:
    ---------
    同步环境（线程/进程）:
        - acquire(timeout): 阻塞获取锁
        - release():      释放锁
        - wait(timeout):  条件等待（需已获得锁）
        - notify(n):      唤醒n个等待者
        - notify_all():   唤醒所有等待者
        - with 上下文管理器

    异步环境（协程/asyncio）:
        - aacquire(timeout):        异步获取锁
        - arelease():              异步释放锁
        - a_wait(timeout):     条件异步等待
        - anotify(n):         唤醒n个协程
        - anotify_all():      唤醒全部协程
        - async with 上下文管理器
    """

    def acquire(self, timeout: Union[float, int]) -> bool: ...

    def release(self) -> None: ...

    def wait(self, timeout: Union[float, int]) -> bool: ...

    def notify(self, n: int = 1) -> None: ...

    def notify_all(self) -> None: ...

    def __enter__(self) -> ISyncLock: ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...

    async def aacquire(self, timeout: Union[float, int]) -> bool: ...

    async def arelease(self) -> None: ...

    async def a_wait(self, timeout: float | int) -> bool: ...

    async def anotify(self, n: int = 1) -> None: ...

    async def anotify_all(self) -> None: ...

    def acontext(self) -> AsyncContextManager[Any]: ...
