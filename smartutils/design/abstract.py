from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from functools import total_ordering
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
    "TClosable",
    "TTransactional",
    "AsyncClosableProtocol",
    "AsyncHealthCheckProtocol",
    "AsyncHealthCheckClosableProtocol",
    "AsyncTransactionalProtocol",
    "TAsyncClosable",
    "TAsyncTransactional",
]

T = TypeVar("T")


@total_ordering
class AbstractComparable(ABC):
    @abstractmethod
    def __eq__(self, other) -> bool: ...

    @abstractmethod
    def __lt__(self, other) -> bool: ...


TAbstractComparable = TypeVar("TAbstractComparable", bound=AbstractComparable)


@runtime_checkable
class IterableProtocol(Protocol[T]):  # type: ignore
    def __iter__(self) -> Iterator[T]: ...


TIterable = TypeVar("TIterable", bound=IterableProtocol)


@runtime_checkable
class ClosableProtocol(Protocol):
    def close(self) -> None: ...


TClosable = TypeVar("TClosable", bound=ClosableProtocol)


@runtime_checkable
class HealthCheckProtocol(Protocol):
    def ping(self) -> bool: ...


@runtime_checkable
class HealthCheckClosableProtocol(ClosableProtocol, HealthCheckProtocol, Protocol):
    pass


@runtime_checkable
class TransactionalProtocol(ClosableProtocol, Protocol):
    def db(self, use_transaction: bool) -> AbstractContextManager[Any]: ...


TTransactional = TypeVar("TTransactional", bound=TransactionalProtocol)


# 异步
@runtime_checkable
class AsyncClosableProtocol(Protocol):
    async def close(self) -> None: ...


TAsyncClosable = TypeVar("TAsyncClosable", bound=AsyncClosableProtocol)


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


TAsyncTransactional = TypeVar("TAsyncTransactional", bound=AsyncTransactionalProtocol)


def _gen_method(name: str) -> Callable:
    def method(self, *args, **kwargs):
        return getattr(self._proxy, name)(*args, **kwargs)

    return method


def proxy_method(cls: type, methods: List[str]):
    # === 批量自动转发体(仅实现, 不影响类型提示) ===

    for _name in methods:
        setattr(cls, _name, _gen_method(_name))
