import asyncio
from typing import Union

from smartutils.design.abstract import proxy_method
from smartutils.design.condition.abstract import AsyncConditionProtocol


class AsyncioCondition(AsyncConditionProtocol):
    def __init__(self, timeout: Union[float, int] = 30 * 60) -> None:
        self._timeout = timeout
        self._proxy = asyncio.Condition()
        super().__init__()

    async def acquire(self, *, timeout: Union[float, int]) -> bool:
        try:
            await asyncio.wait_for(self._proxy.acquire(), timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def wait(self, *, timeout: Union[float, int]) -> bool:
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


proxy_method(AsyncioCondition, ["release", "notify", "notify_all"])
# print(isinstance(AsyncioCondition(), AsyncConditionProtocol))
