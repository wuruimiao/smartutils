import threading
from queue import Empty, Full, Queue
from typing import Any, Callable

from smartutils.config.schema.pool import PoolConf
from smartutils.infra.resource.abstract import AbstractSyncResource
from smartutils.infra.resource.pool.storage.abstract_sync import AbstractSyncPoolStorage
from smartutils.infra.resource.pool.storage.obj import PoolSyncObjectWrapper


class ThreadPoolStorage(AbstractSyncPoolStorage):
    def __init__(self, *, conf: PoolConf, maker: Callable[[], Any]):
        self._pool: Queue[PoolSyncObjectWrapper[AbstractSyncResource]] = Queue()
        lock = threading.Lock()
        super().__init__(conf=conf, maker=maker, lock=lock, total=0)

    def start_background_task(self, fn):
        threading.Thread(target=fn, daemon=True).start()

    def safe_pop(
        self, timeout: int
    ) -> PoolSyncObjectWrapper[AbstractSyncResource] | None:
        try:
            return self._pool.get(timeout=timeout)
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
        # TODO:
        pass
