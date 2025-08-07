from contextlib import AbstractContextManager
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    Iterator,
    List,
    Protocol,
    TypeVar,
    runtime_checkable,
)

__all__ = [
    "ClosableProtocol",
    "HealthCheckProtocol",
    "HealthCheckClosableProtocol",
    "TransactionalProtocol",
    "ClosableT",
    "TransactionalT",
    "AsyncClosableProtocol",
    "AsyncHealthCheckProtocol",
    "AsyncHealthCheckClosableProtocol",
    "AsyncTransactionalProtocol",
    "AsyncClosableT",
    "AsyncTransactionalT",
]

T = TypeVar("T")


@runtime_checkable
class IterableProtocol(Protocol[T]):  # type: ignore
    def __iter__(self) -> Iterator[T]: ...


IterableT = TypeVar("IterableT", bound=IterableProtocol)


@runtime_checkable
class ClosableProtocol(Protocol):
    def close(self) -> None: ...


ClosableT = TypeVar("ClosableT", bound=ClosableProtocol)


@runtime_checkable
class HealthCheckProtocol(Protocol):
    def ping(self) -> bool: ...


@runtime_checkable
class HealthCheckClosableProtocol(ClosableProtocol, HealthCheckProtocol, Protocol):
    pass


@runtime_checkable
class TransactionalProtocol(ClosableProtocol, Protocol):
    def db(self, use_transaction: bool) -> AbstractContextManager[Any]: ...


TransactionalT = TypeVar("TransactionalT", bound=TransactionalProtocol)


# 异步
@runtime_checkable
class AsyncClosableProtocol(Protocol):
    async def close(self) -> None: ...


AsyncClosableT = TypeVar("AsyncClosableT", bound=AsyncClosableProtocol)


@runtime_checkable
class AsyncHealthCheckProtocol(Protocol):
    async def ping(self) -> bool: ...


@runtime_checkable
class AsyncHealthCheckClosableProtocol(
    AsyncClosableProtocol, AsyncHealthCheckProtocol, Protocol
):
    pass


@runtime_checkable
class AsyncTransactionalProtocol(AsyncClosableProtocol, Protocol):
    def db(self, use_transaction: bool) -> AsyncContextManager[Any]: ...


AsyncTransactionalT = TypeVar("AsyncTransactionalT", bound=AsyncTransactionalProtocol)


def _gen_method(name: str) -> Callable:
    def method(self, *args, **kwargs):
        return getattr(self._proxy, name)(*args, **kwargs)

    return method


def proxy_method(cls: type, methods: List[str]):
    # === 批量自动转发体(仅实现, 不影响类型提示) ===

    for _name in methods:
        setattr(cls, _name, _gen_method(_name))
