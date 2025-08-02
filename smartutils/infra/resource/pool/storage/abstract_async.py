import asyncio
import time
from abc import ABC, abstractmethod
from typing import AsyncContextManager, Awaitable, Callable, Generic, Iterable, Optional

from smartutils.config.schema.pool import PoolConf
from smartutils.infra.resource.abstract import (
    AbstractAsyncResource,
    AbstractAsyncResourceT,
)
from smartutils.infra.resource.pool.storage.obj import PoolAsyncObjectWrapper


class AbstractAsyncPoolStorage(ABC, Generic[AbstractAsyncResourceT]):
    def __init__(
        self,
        *,
        conf: PoolConf,
        maker: Callable[[], Awaitable[AbstractAsyncResource]],
        lock,
        total,
    ):
        self._conf = conf
        self._maker = maker
        self._lock = lock
        self._total = total
        super().__init__()

    @abstractmethod
    async def start_background_task(self, fn): ...

    @abstractmethod
    async def safe_pop(
        self,
    ) -> Optional[PoolAsyncObjectWrapper[AbstractAsyncResource]]: ...

    @abstractmethod
    async def safe_push(
        self, wrap: PoolAsyncObjectWrapper[AbstractAsyncResource]
    ) -> bool: ...

    @abstractmethod
    async def safe_remove(
        self, wrap: PoolAsyncObjectWrapper[AbstractAsyncResource]
    ): ...

    @property
    async def total(self) -> int:
        async with self._lock:
            return self._total

    async def dec_total(self) -> None:
        async with self._lock:
            self._total -= 1

    async def inc_total(self) -> None:
        async with self._lock:
            self._total += 1

    async def acquire(self) -> Optional[AbstractAsyncResource]:
        wrap = await self.safe_pop()
        if wrap is not None:
            return wrap.obj

        total = await self.total
        if total >= self._conf.max_pool_size():
            return None

        await self.inc_total()
        return await self._maker()

    async def release(self, obj: AbstractAsyncResource):
        total = await self.total
        wrap = PoolAsyncObjectWrapper(
            obj, total < self._conf.min_pool_size(), time.time()
        )
        result = await self.safe_push(wrap)
        if not result:
            await wrap.close()

    # async def reap(self) -> None:
    #     now = time.time()
    #     remove_list = []
    #     async with self.lock():
    #         all_objects = self.all_objects

    #     for wrap in all_objects:
    #         if wrap.is_overflow and (now - wrap.ts) > self._conf.pool_recycle:
    #             remove_list.append(wrap)

    #     await self.close(remove_list)

    # async def close(self, remove_list=None):
    #     remove_list = remove_list or self.all_objects
    #     for wrap in remove_list:
    #         await wrap.close()
    #         async with self.lock():
    #             await self.safe_remove(wrap)
    #             self.dec_total()
