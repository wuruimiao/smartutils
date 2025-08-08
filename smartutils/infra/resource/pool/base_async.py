import sys
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Optional, Union

from smartutils.design import MyBase
from smartutils.design.abstract import (
    AsyncClosableProtocol,
    IterableProtocol,
    TAsyncClosable,
)
from smartutils.design.condition_container.abstract import (
    AsyncConditionContainerProtocol,
)
from smartutils.infra.resource.pool.abstract import AsyncResourcePoolProtocol
from smartutils.log import logger


class AsyncResourcePoolBase(
    MyBase, AsyncResourcePoolProtocol[TAsyncClosable], AsyncClosableProtocol
):
    def __init__(
        self, *, container: AsyncConditionContainerProtocol[TAsyncClosable]
    ) -> None:
        self._container = container
        super().__init__()

    async def acquire(
        self, timeout: Optional[Union[float, int]] = None
    ) -> Optional[TAsyncClosable]:
        timeout = timeout or sys.maxsize
        return await self._container.get(timeout=timeout, block=timeout is None)

    async def release(
        self, resource: TAsyncClosable, timeout: Optional[Union[float, int]] = None
    ) -> None:
        timeout = timeout or sys.maxsize
        if not await self._container.put(
            resource, timeout=timeout, block=timeout is None
        ):
            logger.error(
                "{name} release {resource} fail, will close it.",
                name=self.name,
                resource=resource,
            )
            await resource.close()

    async def close(self):
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
            await item.close()

        if isinstance(self._container, AsyncClosableProtocol):
            await self._container.close()

    def use(
        self, timeout: Optional[Union[float, int]] = None
    ) -> AbstractAsyncContextManager:
        pool = self

        @asynccontextmanager
        async def _ctx():
            resource = await pool.acquire(timeout=timeout)
            try:
                yield resource
            finally:
                if resource:
                    await pool.release(resource, timeout=timeout)

        return _ctx()
