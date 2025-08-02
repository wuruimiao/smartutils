import time
from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, Optional

from smartutils.config.schema.pool import PoolConf
from smartutils.infra.resource.abstract import AbstractResourceT
from smartutils.infra.resource.pool.base_obj import PoolObjectWrapper


class AbstractPoolState(ABC, Generic[AbstractResourceT]):
    def __init__(
        self, *, conf: PoolConf, maker: Callable[[], AbstractResourceT]
    ) -> None:
        self._conf = conf
        self._maker = maker
        super().__init__()

    @property
    def pool_recycle(self) -> int:
        return self._conf.pool_recycle

    @property
    def pool_timeout(self) -> int:
        return self._conf.pool_timeout

    @abstractmethod
    def pop(self) -> Optional[PoolObjectWrapper[AbstractResourceT]]:
        """
        弹出一个池对象包装器。
        :return: PoolObjectWrapper[AbstractResourceT] 或 None（若池空）
        """
        ...

    @abstractmethod
    def push(self, wrap: PoolObjectWrapper[AbstractResourceT]):
        """
        向池中放回一个对象包装器。
        :param wrap: 对象包装器
        """
        ...

    @abstractmethod
    def remove(self, wrap: PoolObjectWrapper[AbstractResourceT]): ...

    @property
    @abstractmethod
    def all_objects(self) -> Iterable[PoolObjectWrapper[AbstractResourceT]]: ...

    @property
    @abstractmethod
    def total(self) -> int:
        """
        返回当前池内（含溢出）总对象数。
        :return: 数量
        """
        ...

    @abstractmethod
    def dec_total(self) -> None:
        """
        对象总数-1。
        """
        ...

    @abstractmethod
    def inc_total(self) -> None:
        """
        对象总数+1。
        """
        ...

    def acquire(self) -> Optional[AbstractResourceT]:
        """
        创建一个包装对象。
        :param obj: 池中实际对象
        :return: 包装器
        """
        wrap = self.pop()
        if wrap is not None:
            return wrap.obj

        if self.total >= self._conf.max_pool_size():
            return None

        self.inc_total()
        return self._maker()

    def release(self, obj: AbstractResourceT):
        wrap = PoolObjectWrapper(
            obj, self.total < self._conf.min_pool_size(), time.time()
        )
        self.push(wrap)

    def reap(self) -> None:
        """
        清理溢出和超时闲置对象。
        """
        now = time.time()
        remove_list = []
        for wrap in self.all_objects:
            if wrap.is_overflow and (now - wrap.ts) > self._conf.pool_recycle:
                remove_list.append(wrap)
        self.close(remove_list)

    def close(self, remove_list=None):
        remove_list = remove_list or self.all_objects
        for wrap in remove_list:
            self.remove(wrap)
            self.dec_total()
            wrap.close()
