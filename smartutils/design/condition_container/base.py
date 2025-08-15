import time
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from email_validator import DEFAULT_TIMEOUT

from smartutils.design._iter import adrive_steps, drive_steps
from smartutils.design.abstract.common import QueueContainerProtocol
from smartutils.design.condition.abstract import ConditionProtocol
from smartutils.design.condition_container.abstract import ConditionContainerProtocol

T = TypeVar("T")


class ConditionContainerBase(Generic[T]):
    def __init__(
        self, *, container: QueueContainerProtocol[T], condition: ConditionProtocol
    ) -> None:
        self._proxy = container
        self._cond = condition
        super().__init__()

    # def __getattr__(self, name):
    #     return getattr(self._proxy, name)

    def _get_logic_driver(
        self, block: bool, timeout
    ) -> Generator[Tuple[Callable[..., Any], Dict[str, Any]], Any, Optional[T]]:
        start = time.monotonic()

        acquired = yield (self._cond.acquire, {"block": block, "timeout": timeout})
        if not acquired:
            return None

        timeout = timeout or DEFAULT_TIMEOUT

        try:
            if not block:
                if self._proxy.empty():
                    return None
                return self._proxy.get()

            while self._proxy.empty():
                remaining = timeout - (time.monotonic() - start)
                if remaining <= 0:
                    return None
                # 虚假唤醒会继续判断空,False则是超时
                notified = yield (self._cond.wait, {"timeout": remaining})
                if not notified:
                    return None

            return self._proxy.get()
        finally:
            self._cond.release()

    def _put_logic_driver(
        self, value: T, block: bool, timeout
    ) -> Generator[Tuple[Callable[..., Any], Dict[str, Any]], Any, Optional[bool]]:
        start = time.monotonic()

        acquired = yield (self._cond.acquire, {"block": block, "timeout": timeout})
        if not acquired:
            return False

        timeout = timeout or DEFAULT_TIMEOUT

        try:
            if not block:
                if self._proxy.full():
                    return False
                return self._proxy.put(value)

            while self._proxy.full():
                remaining = timeout - (time.monotonic() - start)
                if remaining <= 0:
                    return False
                # 虚假唤醒会继续判断满,False则是超时
                notified = yield (self._cond.wait, {"timeout": remaining})
                if not notified:
                    return False

            self._proxy.put(value)
            self._cond.notify()
        finally:
            self._cond.release()
        return True

    def empty(self) -> bool:
        return self._proxy.empty()

    def full(self) -> bool:
        return self._proxy.full()

    def qsize(self) -> int:
        return self._proxy.qsize()


class ConditionContainer(ConditionContainerBase[T], ConditionContainerProtocol[T]):
    def get(
        self, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> Optional[T]:
        return drive_steps(self._get_logic_driver(block, timeout))

    def put(
        self, value: T, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> bool:
        return drive_steps(self._put_logic_driver(value, block, timeout))


class AsyncConditionContainer(ConditionContainerBase[T], ConditionContainerProtocol[T]):
    async def get(
        self, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> Optional[T]:
        return await adrive_steps(self._get_logic_driver(block, timeout))

    async def put(
        self, value: T, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> bool:
        return await adrive_steps(self._put_logic_driver(value, block, timeout))
