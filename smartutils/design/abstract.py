from contextlib import AbstractContextManager
from typing import Any, AsyncContextManager, Protocol, TypeVar, runtime_checkable

__all__ = [
    "HealthClosable",
    "HealthClosableT",
    "Transactional",
    "TransactionalT",
    "AsyncHealthClosable",
    "AsyncHealthClosableT",
    "AsyncTransactional",
    "AsyncTransactionalT",
]


# 同步
@runtime_checkable
class HealthClosable(Protocol):
    def close(self) -> None: ...
    def ping(self) -> bool: ...


HealthClosableT = TypeVar("HealthClosableT", bound=HealthClosable)


@runtime_checkable
class Transactional(HealthClosable, Protocol):
    def db(self, use_transaction: bool) -> AbstractContextManager[Any]: ...


TransactionalT = TypeVar("TransactionalT", bound=Transactional)


# 异步
@runtime_checkable
class AsyncHealthClosable(Protocol):
    async def close(self) -> None: ...
    async def ping(self) -> bool: ...


AsyncHealthClosableT = TypeVar("AsyncHealthClosableT", bound=AsyncHealthClosable)


@runtime_checkable
class AsyncTransactional(AsyncHealthClosable, Protocol):
    def db(self, use_transaction: bool) -> AsyncContextManager[Any]: ...


AsyncTransactionalT = TypeVar("AsyncTransactionalT", bound=AsyncTransactional)
