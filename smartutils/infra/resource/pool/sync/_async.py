import asyncio
from typing import AsyncContextManager

from smartutils.infra.resource.pool.sync.abstract import PoolSyncAsync


class PoolSyncAsyncio(PoolSyncAsync):
    is_async = True

    def __init__(self):
        self._lock = asyncio.Lock()
        self._cond = asyncio.Condition(self._lock)

    def lock(self) -> AsyncContextManager:
        return self._lock

    async def wait(self, timeout=None):
        try:
            await asyncio.wait_for(self._cond.wait(), timeout)
        except asyncio.TimeoutError:
            ...

    async def notify(self):
        self._cond.notify()

    def start_background_task(self, fn):
        asyncio.get_event_loop().create_task(fn())
