from __future__ import annotations

import asyncio
from typing import Awaitable, Optional, Union

from smartutils.design._class import MyBase
from smartutils.design.abstract.common import Proxy
from smartutils.design.condition.abstract import ConditionProtocol
from smartutils.design.const import DEFAULT_TIMEOUT
from smartutils.error.sys import LibraryUsageError


class AsyncioCondition(MyBase, ConditionProtocol):
    def __init__(self, timeout: Union[float, int] = DEFAULT_TIMEOUT) -> None:
        self._timeout = timeout
        self._proxy = asyncio.Condition()
        super().__init__()

    def acquire(
        self, *, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> Awaitable[bool]:
        return self._acquire(block=block, timeout=timeout)

    async def _acquire(
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

    def wait(self, *, timeout: Optional[Union[float, int]] = None) -> Awaitable[bool]:
        return self._wait(timeout=timeout)

    async def _wait(self, *, timeout: Optional[Union[float, int]] = None) -> bool:
        if timeout is None:
            return await self._proxy.wait()
        try:
            await asyncio.wait_for(self._proxy.wait(), timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def __aenter__(self) -> AsyncioCondition:
        await self.acquire(timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._proxy.release()

    def __enter__(self):
        raise LibraryUsageError(f"{self.name} does not support sync with")

    def __exit__(self, exc_type, exc_val, exc_tb): ...

    def release(self) -> None: ...
    def notify(self, n: int = 1) -> None: ...
    def notify_all(self) -> None: ...


Proxy.method(AsyncioCondition, ["release", "notify", "notify_all"])
# print(isinstance(AsyncioCondition(), AsyncConditionProtocol))
