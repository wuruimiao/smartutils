import time
from typing import Iterator, Optional, TypeVar, Union

from smartutils.design.abstract import IterableProtocol
from smartutils.design.condition.abstract import AsyncConditionProtocol
from smartutils.design.condition_container.abstract import (
    AsyncConditionContainerProtocol,
)
from smartutils.design.const import DEFAULT_TIMEOUT
from smartutils.design.container.abstract import AbstractContainer

T = TypeVar("T")


class AsyncConditionContainer(AsyncConditionContainerProtocol[T], IterableProtocol[T]):
    def __init__(
        self, *, container: AbstractContainer[T], condition: AsyncConditionProtocol
    ) -> None:
        self._proxy = container
        self._cond = condition
        super().__init__()

    def __getattr__(self, name):
        return getattr(self._proxy, name)

    async def get(
        self, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> Optional[T]:
        start = time.monotonic()
        if not await self._cond.acquire(block=block, timeout=timeout):
            return None

        timeout = timeout or DEFAULT_TIMEOUT

        try:
            if not block:
                if self._proxy.empty():
                    return None
                return self._proxy.get()

            while self._proxy.empty():
                remaining = timeout - (time.monotonic() - start)
                if remaining <= 0:  # pragma: no cover
                    return None
                notified = await self._cond.wait(timeout=remaining)
                if not notified:
                    return None
            return self._proxy.get()
        finally:
            self._cond.release()

    async def put(
        self,
        value: T,
        block: bool = True,
        timeout: Optional[Union[float, int]] = None,
    ) -> bool:
        if not await self._cond.acquire(block=block, timeout=timeout):
            return False

        try:
            self._proxy.put(value)
            self._cond.notify()
        finally:
            self._cond.release()
        return True

    def empty(self) -> bool:
        return self._proxy.empty()

    def __iter__(self) -> Iterator[T]:
        return iter(self._proxy)
