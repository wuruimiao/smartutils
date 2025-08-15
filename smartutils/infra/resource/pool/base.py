from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    asynccontextmanager,
    contextmanager,
)
from typing import Awaitable, Callable, Generic, Iterable, Optional, TypeVar, Union

from smartutils.config.schema.pool import PoolConf
from smartutils.design import MyBase
from smartutils.design._iter import adrive_steps, drive_steps
from smartutils.design.abstract._async import AsyncClosableProtocol, TAsyncClosable
from smartutils.design.abstract._sync import ClosableProtocol, TClosable
from smartutils.design.condition_container.abstract import ConditionContainerProtocol
from smartutils.infra.resource.pool.abstract import ResourcePoolProtocol
from smartutils.log import logger

T = TypeVar("T")


class _ResourcePoolBase(MyBase, Generic[T]):
    def __init__(
        self,
        *,
        container: ConditionContainerProtocol,
        conf: PoolConf,
        resource_maker: Callable[..., T],
    ) -> None:
        self._container = container
        self._conf = conf
        self._maker = resource_maker
        super().__init__()

    def _init_logic_driver(self):
        for _ in range(self._conf.min_pool_size()):
            yield (self._container.put, {"block": True})

    def _acquire_logic_driver(self, timeout: Optional[Union[float, int]]):
        item = yield (
            self._container.get,
            {"timeout": timeout, "block": timeout is None},
        )
        if item:
            return item

    def _release_logic_driver(self, resource, timeout):
        ok = yield (
            self._container.put,
            {"value": resource, "timeout": timeout, "block": timeout is None},
        )
        if not ok:
            logger.error(f"{self.name} release {resource} fail, will close it.")
            yield (resource.close, {})

    def _close_logic_driver(self):
        items = []
        if isinstance(self._container, Iterable):
            items = list(self._container)
        else:
            while not self._container.empty():
                item = yield (self._container.get, {"timeout": 1})
                if not item:
                    break
                items.append(item)

        for item in items:
            yield (item.close, {})

        if isinstance(self._container, ClosableProtocol) or isinstance(
            self._container, AsyncClosableProtocol
        ):
            yield (self._container.close, {})


class ResourcePoolBase(
    _ResourcePoolBase, ResourcePoolProtocol[TClosable], ClosableProtocol
):
    def init(self) -> None:
        return drive_steps(self._init_logic_driver())

    def acquire(
        self, timeout: Optional[Union[float, int]] = None
    ) -> Optional[TClosable]:
        return drive_steps(self._acquire_logic_driver(timeout))

    def release(
        self, resource: TClosable, timeout: Optional[Union[float, int]] = None
    ) -> None:
        return drive_steps(self._release_logic_driver(resource, timeout))

    def close(self):
        return drive_steps(self._close_logic_driver())

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


class AsyncResourcePoolBase(
    _ResourcePoolBase, ResourcePoolProtocol[TAsyncClosable], AsyncClosableProtocol
):
    async def init(self) -> None:
        return await adrive_steps(self._init_logic_driver())

    async def acquire(
        self, timeout: Optional[Union[float, int]] = None
    ) -> Optional[TAsyncClosable]:
        return await adrive_steps(self._acquire_logic_driver(timeout))

    async def release(
        self, resource: TAsyncClosable, timeout: Optional[Union[float, int]] = None
    ) -> None:
        return await adrive_steps(self._release_logic_driver(resource, timeout))

    async def close(self):
        return await adrive_steps(self._close_logic_driver())

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
