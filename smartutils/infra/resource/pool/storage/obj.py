import time
from typing import Generic, Optional

from smartutils.infra.resource.abstract import (
    AbstractAsyncResourceT,
    AbstractSyncResourceT,
)


class PoolSyncObjectWrapper(Generic[AbstractSyncResourceT]):
    def __init__(
        self, obj: AbstractSyncResourceT, is_overflow: bool, ts: Optional[float] = None
    ):
        self.obj = obj
        self.is_overflow = is_overflow
        self.ts = ts or time.time()

    def close(self):
        self.obj.close()


class PoolAsyncObjectWrapper(Generic[AbstractAsyncResourceT]):
    def __init__(
        self, obj: AbstractAsyncResourceT, is_overflow: bool, ts: Optional[float] = None
    ):
        self.obj = obj
        self.is_overflow = is_overflow
        self.ts = ts or time.time()

    async def close(self):
        await self.obj.close()
