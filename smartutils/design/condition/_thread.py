from __future__ import annotations

import threading
from typing import Union

from smartutils.design.abstract import proxy_method
from smartutils.design.condition.abstract import ConditionProtocol


class ThreadCondition(ConditionProtocol):
    def __init__(self, *, timeout: Union[float, int] = 30 * 60) -> None:
        """
        初始化线程同步锁。
        """
        self._timeout = timeout
        self._proxy = threading.Condition()
        super().__init__()

    def __enter__(self) -> ThreadCondition:
        self.acquire(timeout=self._timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

    def acquire(self, *, timeout: Union[float, int]) -> bool: ...
    def release(self) -> None: ...
    def wait(self, *, timeout: float | int | None) -> bool: ...
    def notify(self, n: int = 1) -> None: ...
    def notify_all(self) -> None: ...


proxy_method(ThreadCondition, ["acquire", "release", "wait", "notify", "notify_all"])
# print(isinstance(ThreadCondition(), ConditionProtocol))

# cond = ThreadCondition()
# t = threading.Thread(target=lambda: cond.acquire(timeout=3))
# t.start()
# print(1111)
# cond.acquire(timeout=3)
# t.join()
