from __future__ import annotations

from typing import Awaitable, Optional, Protocol, Union, runtime_checkable


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
        self, *, block: bool = True, timeout: Optional[float] = None
    ) -> Union[bool, Awaitable[bool]]: ...
    def release(self) -> None: ...
    def wait(
        self, *, timeout: Optional[float] = None
    ) -> Union[bool, Awaitable[bool]]: ...
    def notify(self, n: int = 1) -> None: ...
    def notify_all(self) -> None: ...
    def __enter__(self) -> ConditionProtocol: ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...
    async def __aenter__(self) -> ConditionProtocol: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
