from contextlib import AbstractContextManager
from typing import Any, AsyncContextManager, Protocol, TypeVar, runtime_checkable

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


@runtime_checkable
class ClosableProtocol(Protocol):
    def close(self) -> None: ...


@runtime_checkable
class HealthCheckProtocol(Protocol):
    def ping(self) -> bool: ...


@runtime_checkable
class HealthCheckClosableProtocol(ClosableProtocol, HealthCheckProtocol, Protocol):
    pass


ClosableT = TypeVar("ClosableT", bound=ClosableProtocol)


@runtime_checkable
class TransactionalProtocol(ClosableProtocol, Protocol):
    def db(self, use_transaction: bool) -> AbstractContextManager[Any]: ...


TransactionalT = TypeVar("TransactionalT", bound=TransactionalProtocol)


# 异步
@runtime_checkable
class AsyncClosableProtocol(Protocol):
    async def close(self) -> None: ...


@runtime_checkable
class AsyncHealthCheckProtocol(Protocol):
    async def ping(self) -> bool: ...


@runtime_checkable
class AsyncHealthCheckClosableProtocol(
    AsyncClosableProtocol, AsyncHealthCheckProtocol, Protocol
):
    pass


AsyncClosableT = TypeVar("AsyncClosableT", bound=AsyncClosableProtocol)


@runtime_checkable
class AsyncTransactionalProtocol(AsyncClosableProtocol, Protocol):
    def db(self, use_transaction: bool) -> AsyncContextManager[Any]: ...


AsyncTransactionalT = TypeVar("AsyncTransactionalT", bound=AsyncTransactionalProtocol)
