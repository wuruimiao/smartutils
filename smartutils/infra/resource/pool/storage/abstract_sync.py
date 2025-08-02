import time
from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, Optional

from smartutils.config.schema.pool import PoolConf
from smartutils.infra.resource.abstract import (
    AbstractSyncResource,
    AbstractSyncResourceT,
)
from smartutils.infra.resource.pool.storage.obj import PoolSyncObjectWrapper


class AbstractSyncPoolStorage(ABC, Generic[AbstractSyncResourceT]):
    def __init__(
        self,
        *,
        conf: PoolConf,
        maker: Callable[[], AbstractSyncResource],
        lock,
        total,
    ):
        self._conf = conf
        self._maker = maker
        self._lock = lock
        self._total = total
        super().__init__()

    @abstractmethod
    def start_background_task(self, fn): ...

    @abstractmethod
    def safe_pop(
        self, timeout: int
    ) -> Optional[PoolSyncObjectWrapper[AbstractSyncResource]]: ...

    @abstractmethod
    def safe_push(
        self, wrap: PoolSyncObjectWrapper[AbstractSyncResource], timeout: int
    ) -> bool: ...

    @abstractmethod
    def safe_remove(self, wrap: PoolSyncObjectWrapper[AbstractSyncResource]): ...

    @property
    def total(self) -> int:
        with self._lock:
            return self._total

    def safe_dec_total(self) -> None:
        with self._lock:
            self._total -= 1

    def safe_inc_total(self) -> None:
        with self._lock:
            self._total += 1

    def acquire(self, timeout: int) -> Optional[AbstractSyncResource]:
        wrap = self.safe_pop(timeout)
        if wrap is not None:
            return wrap.obj

        if self.total >= self._conf.max_pool_size():
            return None

        self.safe_inc_total()
        return self._maker()

    def release(self, obj: AbstractSyncResource, timeout: int):
        wrap = PoolSyncObjectWrapper(
            obj, self.total < self._conf.min_pool_size(), time.time()
        )
        result = self.safe_push(wrap, timeout)
        if not result:
            wrap.close()
            self.safe_dec_total()

    # def reap(self) -> None:
    #     now = time.time()
    #     remove_list = []
    #     all_objects = self.all_objects

    #     for wrap in all_objects:
    #         if wrap.is_overflow and (now - wrap.ts) > self._conf.pool_recycle:
    #             remove_list.append(wrap)

    #     self.close(remove_list)

    # def close(self, remove_list=None):
    #     remove_list = remove_list or self.all_objects
    #     for wrap in remove_list:
    #         wrap.close()
    #         self.safe_remove(wrap)
    #         self.safe_dec_total()
