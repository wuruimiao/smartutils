from __future__ import annotations

from typing import Optional, Protocol, Union, runtime_checkable


@runtime_checkable
class ConditionProtocol(Protocol):
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
    """

    def acquire(
        self, *, blocking: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> bool: ...

    def release(self) -> None: ...

    def wait(self, *, timeout: Optional[Union[float, int]] = None) -> bool: ...

    def notify(self, n: int = 1) -> None: ...

    def notify_all(self) -> None: ...

    def __enter__(self) -> ConditionProtocol: ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...


@runtime_checkable
class AsyncConditionProtocol(Protocol):
    """
    异步环境（协程/asyncio）:
    - aacquire(timeout):        异步获取锁
    - arelease():              异步释放锁
    - a_wait(timeout):     条件异步等待
    - anotify(n):         唤醒n个协程
    - anotify_all():      唤醒全部协程
    - async with 上下文管理器
    """

    async def acquire(
        self, *, blocking: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> bool: ...

    def release(self) -> None: ...

    async def wait(self, *, timeout: Optional[Union[float, int]] = None) -> bool: ...

    def notify(self, n: int = 1) -> None: ...

    def notify_all(self) -> None: ...

    async def __aenter__(self): ...

    async def __aexit__(self, exc_type, exc, tb): ...
