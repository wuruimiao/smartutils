import time
from typing import Optional, TypeVar, Union

from smartutils.design.condition.abstract import (
    AsyncConditionProtocol,
    ConditionProtocol,
)
from smartutils.design.condition_container.abstract import (
    AsyncConditionContainerProtocol,
    ConditionContainerProtocol,
)
from smartutils.design.container.abstract import AbstractContainer

T = TypeVar("T")


# 类比queue.Queue()
class ConditionContainer(ConditionContainerProtocol[T]):
    def __init__(
        self, *, container: AbstractContainer[T], condition: ConditionProtocol
    ) -> None:
        self._container = container
        self._cond = condition
        super().__init__()

    def __getattr__(self, name):
        return getattr(self._container, name)

    def get(self, timeout: Union[float, int], block: bool = True) -> Optional[T]:
        start = time.monotonic()
        if not self._cond.acquire(timeout=timeout):
            return None

        try:
            if not block:
                if self._container.empty():
                    return None
                return self._container.get()

            while self._container.empty():
                remaining = timeout - (time.monotonic() - start)
                if remaining <= 0:  # pragma: no cover
                    return None
                notified = self._cond.wait(timeout=remaining)
                if not notified:
                    return None
            return self._container.get()
        finally:
            self._cond.release()

    def put(self, value: T, timeout: Union[float, int], block: bool = True) -> bool:
        if not self._cond.acquire(timeout=timeout):
            return False

        try:
            self._container.put(value)
            self._cond.notify()
        finally:
            self._cond.release()
        return True

    def empty(self) -> bool:
        return self._container.empty()


class AsyncConditionContainer(AsyncConditionContainerProtocol[T]):
    def __init__(
        self, *, container: AbstractContainer[T], condition: AsyncConditionProtocol
    ) -> None:
        self._container = container
        self._cond = condition
        super().__init__()

    def __getattr__(self, name):
        return getattr(self._container, name)

    async def get(self, timeout: Union[float, int], block: bool = True) -> Optional[T]:
        start = time.monotonic()
        if not await self._cond.acquire(timeout=timeout):
            return None

        try:
            if not block:
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
        self, value: T, timeout: Union[float, int], block: bool = True
    ) -> bool:
        if not await self._cond.acquire(timeout=timeout):
            return False

        try:
            self._container.put(value)
            self._cond.notify()
        finally:
            self._cond.release()
        return True

    def empty(self) -> bool:
        return self._container.empty()
