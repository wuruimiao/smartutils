from typing import Callable

from smartutils.config.schema.pool import PoolConf
from smartutils.infra.resource.abstract import AbstractAsyncResourceT
from smartutils.infra.resource.pool.base_pool import AsyncPoolBase, SyncPoolBase
from smartutils.infra.resource.pool.state._manager import PoolManagerState
from smartutils.infra.resource.pool.state._queue import PoolQueueState
from smartutils.infra.resource.pool.sync._async import PoolSyncAsyncio
from smartutils.infra.resource.pool.sync._process import PoolSyncProcess
from smartutils.infra.resource.pool.sync._thread import PoolSyncThread


class ThreadPool(SyncPoolBase[AbstractAsyncResourceT]):
    def __init__(self, conf: PoolConf, maker: Callable[[], AbstractAsyncResourceT]):
        super().__init__(PoolQueueState(conf=conf, maker=maker), PoolSyncThread())


class ProcessPool(SyncPoolBase[AbstractAsyncResourceT]):
    def __init__(
        self, conf: PoolConf, maker: Callable[[], AbstractAsyncResourceT], manager
    ):
        super().__init__(
            PoolManagerState(conf=conf, maker=maker, manager=manager),
            PoolSyncProcess(manager=manager),
        )


class AsyncioPool(AsyncPoolBase[AbstractAsyncResourceT]):
    def __init__(self, conf: PoolConf, maker: Callable[[], AbstractAsyncResourceT]):
        super().__init__(PoolQueueState(conf=conf, maker=maker), PoolSyncAsyncio())
