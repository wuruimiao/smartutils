from __future__ import annotations

import threading
from typing import Optional, Union

from smartutils.design.abstract import proxy_method
from smartutils.design.condition.abstract import ConditionProtocol
from smartutils.design.const import DEFAULT_TIMEOUT


class ThreadCondition(ConditionProtocol):
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

    def acquire(
        self, *, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> bool:
        timeout = timeout if block else None
        return self._proxy.acquire(block=block, timeout=timeout)  # type: ignore

    def release(self) -> None: ...
    def wait(self, *, timeout: Optional[Union[float, int]] = None) -> bool: ...
    def notify(self, n: int = 1) -> None: ...
    def notify_all(self) -> None: ...


proxy_method(ThreadCondition, ["release", "wait", "notify", "notify_all"])
# print(isinstance(ThreadCondition(), ConditionProtocol))

# cond = ThreadCondition()
# t = threading.Thread(target=lambda: cond.acquire(timeout=3))
# t.start()
# print(1111)
# cond.acquire(timeout=3)
# t.join()
