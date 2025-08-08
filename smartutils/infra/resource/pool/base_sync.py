import sys
from contextlib import AbstractContextManager, contextmanager
from typing import Optional, Union

from smartutils.config.schema.pool import PoolConf
from smartutils.design import MyBase
from smartutils.design.abstract import (
    ClosableProtocol,
    IterableProtocol,
    TClosable,
)
from smartutils.design.condition_container.abstract import ConditionContainerProtocol
from smartutils.infra.resource.pool.abstract import ResourcePoolProtocol
from smartutils.log import logger


class ResourcePoolBase(MyBase, ResourcePoolProtocol[TClosable], ClosableProtocol):
    def __init__(
        self, *, container: ConditionContainerProtocol[TClosable], conf: PoolConf
    ) -> None:
        self._container = container
        super().__init__()

    def acquire(
        self, timeout: Optional[Union[float, int]] = None
    ) -> Optional[TClosable]:
        timeout = timeout or sys.maxsize
        return self._container.get(timeout=timeout, block=timeout is None)

    def release(
        self, resource: TClosable, timeout: Optional[Union[float, int]] = None
    ) -> None:
        timeout = timeout or sys.maxsize
        if not self._container.put(resource, timeout=timeout, block=timeout is None):
            logger.error(
                "{name} release {resource} fail, will close it.",
                name=self.name,
                resource=resource,
            )
            resource.close()

    def close(self):
        items = []
        if isinstance(self._container, IterableProtocol):
            items = list(self._container)
        else:
            while not self._container.empty():
                item = self.acquire(timeout=1)
                if not item:
                    break
                items.append(item)

        for item in items:
            item.close()

        if isinstance(self._container, ClosableProtocol):
            self._container.close()

    def use(
        self, timeout: Optional[Union[float, int]] = None
    ) -> AbstractContextManager:
        pool = self

        @contextmanager
        def _ctx():
            resource = pool.acquire(timeout=timeout)
            try:
                yield resource
            finally:
                if resource:
                    pool.release(resource, timeout=timeout)

        return _ctx()
