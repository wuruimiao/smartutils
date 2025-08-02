import asyncio
import threading
from asyncio import Queue
from collections import deque
from typing import Any, Awaitable, Callable, Deque, Iterable

from smartutils.config.schema.pool import PoolConf
from smartutils.infra.resource.abstract import (
    AbstractAsyncResource,
    AbstractSyncResource,
)
from smartutils.infra.resource.pool.storage.abstract_async import (
    AbstractAsyncPoolStorage,
)
from smartutils.infra.resource.pool.storage.obj import (
    PoolAsyncObjectWrapper,
    PoolSyncObjectWrapper,
)


class AyncioPoolStorage(AbstractAsyncPoolStorage):
    def __init__(
        self,
        *,
        conf: PoolConf,
        maker: Callable[[], Awaitable[AbstractAsyncResource]],
        lock,
    ):
        self._pool: Queue[PoolAsyncObjectWrapper[AbstractAsyncResource]] = Queue()
        lock = asyncio.Lock()
        super().__init__(conf=conf, maker=maker, lock=lock, total=0)

    async def start_background_task(self, fn):
        await fn()

    async def safe_pop(self) -> PoolAsyncObjectWrapper[AbstractAsyncResource] | None:
        await self._pool.get()

    async def safe_push(
        self, wrap: PoolAsyncObjectWrapper[AbstractAsyncResource]
    ) -> bool:
        await self._pool.put(wrap)
        return True

    async def safe_remove(self, wrap: PoolAsyncObjectWrapper[AbstractAsyncResource]):
        # TODO
        pass
