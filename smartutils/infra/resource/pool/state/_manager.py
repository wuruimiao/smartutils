from typing import Callable, Iterable, Optional

from smartutils.config.schema.pool import PoolConf
from smartutils.infra.resource.abstract import AbstractResourceT
from smartutils.infra.resource.pool.base_obj import PoolObjectWrapper
from smartutils.infra.resource.pool.state.abstract import AbstractPoolState


class PoolManagerState(AbstractPoolState[AbstractResourceT]):
    def __init__(
        self, *, conf: PoolConf, maker: Callable[[], AbstractResourceT], manager
    ):
        super().__init__(conf=conf, maker=maker)

        self._pool = manager.list()
        self._total = manager.list([0])
        self._manager = manager

    def pop(self) -> Optional[PoolObjectWrapper]:
        try:
            wrap = self._pool.pop(0)
            return wrap
        except IndexError:
            return None

    def push(self, wrap: PoolObjectWrapper):
        self._pool.append(wrap)

    @property
    def total(self) -> int:
        return self._total[0]

    def dec_total(self) -> None:
        self._total[0] -= 1

    def inc_total(self) -> None:
        self._total[0] += 1

    def remove(self, wrap: PoolObjectWrapper[AbstractResourceT]):
        self._pool.remove(wrap)

    @property
    def all_objects(self) -> Iterable[PoolObjectWrapper[AbstractResourceT]]:
        return list(self._pool)
