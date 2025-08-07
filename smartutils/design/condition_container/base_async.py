import time
from typing import Optional, TypeVar, Union

from smartutils.design.condition.abstract import AsyncConditionProtocol
from smartutils.design.condition_container.abstract import (
    AsyncConditionContainerProtocol,
)
from smartutils.design.const import DEFAULT_TIMEOUT
from smartutils.design.container.abstract import AbstractContainer

T = TypeVar("T")


class AsyncConditionContainer(AsyncConditionContainerProtocol[T]):
    def __init__(
        self, *, container: AbstractContainer[T], condition: AsyncConditionProtocol
    ) -> None:
        self._container = container
        self._cond = condition
        super().__init__()

    def __getattr__(self, name):
        return getattr(self._container, name)

    async def get(
        self, blocking: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> Optional[T]:
        start = time.monotonic()
        if not await self._cond.acquire(blocking=blocking, timeout=timeout):
            return None

        timeout = timeout or DEFAULT_TIMEOUT

        try:
            if not blocking:
                if self._container.empty():
                    return None
                return self._container.get()

            while self._container.empty():
                remaining = timeout - (time.monotonic() - start)
                if remaining <= 0:  # pragma: no cover
                    return None
                notified = await self._cond.wait(timeout=remaining)
                if not notified:
                    return None
            return self._container.get()
        finally:
            self._cond.release()

    async def put(
        self,
        value: T,
        blocking: bool = True,
        timeout: Optional[Union[float, int]] = None,
    ) -> bool:
        if not await self._cond.acquire(blocking=blocking, timeout=timeout):
            return False

        try:
            self._container.put(value)
            self._cond.notify()
        finally:
            self._cond.release()
        return True

    def empty(self) -> bool:
        return self._container.empty()
