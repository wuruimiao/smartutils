from collections import deque
from typing import Callable, Deque, Iterable, Optional

from smartutils.config.schema.pool import PoolConf
from smartutils.infra.resource.abstract import AbstractResourceT
from smartutils.infra.resource.pool.base_obj import PoolObjectWrapper
from smartutils.infra.resource.pool.state.abstract import AbstractPoolState


class PoolQueueState(AbstractPoolState[AbstractResourceT]):
    def __init__(self, *, conf: PoolConf, maker: Callable[[], AbstractResourceT]):
        super().__init__(conf=conf, maker=maker)

        self._pool: Deque[PoolObjectWrapper[AbstractResourceT]] = deque()
        self._total: int = 0

    def pop(self) -> Optional[PoolObjectWrapper[AbstractResourceT]]:
        try:
            return self._pool.popleft()
        except IndexError:
            return None

    def push(self, wrap: PoolObjectWrapper[AbstractResourceT]):
        self._pool.append(wrap)

    def remove(self, wrap: PoolObjectWrapper[AbstractResourceT]):
        self._pool.remove(wrap)

    @property
    def total(self) -> int:
        return self._total

    def dec_total(self):
        self._total -= 1

    def inc_total(self):
        self._total += 1

    @property
    def all_objects(self) -> Iterable[PoolObjectWrapper[AbstractResourceT]]:
        return list(self._pool)
