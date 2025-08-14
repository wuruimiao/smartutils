from __future__ import annotations

import threading
from typing import Optional, Union

from smartutils.design._class import MyBase
from smartutils.design.abstract.common import Proxy
from smartutils.design.condition.abstract import ConditionProtocol
from smartutils.design.const import DEFAULT_TIMEOUT


class ThreadCondition(MyBase, ConditionProtocol):
    def __init__(self, *, timeout: Union[float, int] = DEFAULT_TIMEOUT) -> None:
        """
        初始化线程同步锁。
        """
        self._timeout = timeout
        self._proxy = threading.Condition()
        super().__init__()

    def __enter__(self) -> ThreadCondition:
        self.acquire(block=True, timeout=self._timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

    async def __aenter__(self) -> ThreadCondition:
        self.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.__exit__(exc_type, exc_val, exc_tb)

    def acquire(
        self, *, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> bool:
        if not block:
            return self._proxy.acquire(blocking=False)
        elif timeout is None:
            return self._proxy.acquire(blocking=True)
        return self._proxy.acquire(blocking=block, timeout=timeout)

    def release(self) -> None: ...
    def wait(self, *, timeout: Optional[Union[float, int]] = None) -> bool: ...
    def notify(self, n: int = 1) -> None: ...
    def notify_all(self) -> None: ...


Proxy.method(ThreadCondition, ["release", "wait", "notify", "notify_all"])
# print(isinstance(ThreadCondition(), ConditionProtocol))

# cond = ThreadCondition()
# t = threading.Thread(target=lambda: cond.acquire(timeout=3))
# t.start()
# print(1111)
# cond.acquire(timeout=3)
# t.join()
