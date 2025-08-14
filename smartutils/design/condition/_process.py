from __future__ import annotations

from multiprocessing import Manager
from multiprocessing.managers import SyncManager
from multiprocessing.synchronize import Condition
from typing import Optional, Union

from smartutils.design.abstract.common import Proxy
from smartutils.design.condition.abstract import ConditionProtocol
from smartutils.design.const import DEFAULT_TIMEOUT


class ProcessCondition(ConditionProtocol):
    def __init__(
        self,
        *,
        manager: Optional[SyncManager] = None,
        timeout: Union[float, int] = DEFAULT_TIMEOUT,
    ):
        if manager is None:
            manager = Manager()
            self._manager_owner = True
        else:
            self._manager_owner = False
        self._proxy: Condition = manager.Condition()  # type: ignore
        self._manager = manager
        self._timeout = timeout

    def __enter__(self) -> ProcessCondition:
        self.acquire(block=True, timeout=self._timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        # 若本类创建了 Manager，自动关闭资源
        if self._manager_owner:
            self._manager.shutdown()

    async def __aenter__(self) -> ProcessCondition:
        self.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.__exit__(exc_type, exc_val, exc_tb)

    def acquire(
        self, *, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> bool:
        timeout = timeout if block else 0
        return self._proxy.acquire(timeout=timeout)

    def release(self) -> None: ...
    def wait(self, *, timeout: Optional[Union[float, int]] = None) -> bool: ...
    def notify(self, n: int = 1) -> None: ...
    def notify_all(self) -> None: ...


Proxy.method(ProcessCondition, ["release", "wait", "notify", "notify_all"])

# print(isinstance(ProcessCondition(), ConditionProtocol))
