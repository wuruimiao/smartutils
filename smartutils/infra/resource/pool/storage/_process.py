import multiprocessing
from multiprocessing import Queue
from queue import Empty, Full
from typing import Any, Callable, Iterable

from smartutils.config.schema.pool import PoolConf
from smartutils.infra.resource.abstract import AbstractSyncResource
from smartutils.infra.resource.pool.storage.abstract_sync import AbstractSyncPoolStorage
from smartutils.infra.resource.pool.storage.obj import PoolSyncObjectWrapper


class ProcessPoolStorage(AbstractSyncPoolStorage):
    def __init__(self, *, conf: PoolConf, maker: Callable[[], Any], manager):
        self._pool = Queue()
        lock = manager.Lock()
        self._cond = multiprocessing.Condition(lock)
        self._manager = manager
        super().__init__(
            conf=conf,
            maker=maker,
            lock=lock,
            total=manager.list([0]),
        )

    def start_background_task(self, fn):
        multiprocessing.Process(target=fn, daemon=True).start()

    def safe_pop(
        self, timeout: int
    ) -> PoolSyncObjectWrapper[AbstractSyncResource] | None:
        try:
            wrap = self._pool.get(timeout=timeout)
            return wrap
        except Empty:
            return None

    def safe_push(
        self, wrap: PoolSyncObjectWrapper[AbstractSyncResource], timeout: int
    ) -> bool:
        try:
            self._pool.put(wrap, timeout=timeout)
            return True
        except Full:
            return False

    def safe_remove(self, wrap: PoolSyncObjectWrapper[AbstractSyncResource]):
        # TODO
        ...
