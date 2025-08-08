import asyncio
from typing import Optional, Union

from smartutils.design.abstract.common import Proxy
from smartutils.design.condition.abstract import AsyncConditionProtocol
from smartutils.design.const import DEFAULT_TIMEOUT


class AsyncioCondition(AsyncConditionProtocol):
    def __init__(self, timeout: Union[float, int] = DEFAULT_TIMEOUT) -> None:
        self._timeout = timeout
        self._proxy = asyncio.Condition()
        super().__init__()

    async def acquire(
        self, *, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> bool:
        if not block:
            return await self._proxy.acquire()
        timeout = timeout or self._timeout
        try:
            await asyncio.wait_for(self._proxy.acquire(), timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def wait(self, *, timeout: Optional[Union[float, int]] = None) -> bool:
        timeout = timeout or DEFAULT_TIMEOUT
        try:
            await asyncio.wait_for(self._proxy.wait(), timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def __aenter__(self):
        await self.acquire(timeout=self._timeout)

    async def __aexit__(self, exc_type, exc, tb):
        self._proxy.release()

    def release(self) -> None: ...
    def notify(self, n: int = 1) -> None: ...
    def notify_all(self) -> None: ...


Proxy.method(AsyncioCondition, ["release", "notify", "notify_all"])
# print(isinstance(AsyncioCondition(), AsyncConditionProtocol))
