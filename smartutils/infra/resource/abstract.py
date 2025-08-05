from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Any, AsyncContextManager, Protocol, TypeVar

__all__ = ["AbstractAsyncResource", "AbstractAsyncResourceT"]


class Closable(Protocol):
    def close(self) -> None: ...


ClosableT = TypeVar("ClosableT", bound=Closable)


class AsyncClosable(Protocol):
    async def close(self) -> None: ...


AsyncClosableT = TypeVar("AsyncClosableT", bound=AsyncClosable)


class AbstractAsyncResource(AsyncClosable, ABC):
    @abstractmethod
    async def ping(self) -> bool:
        """健康检查，返回True/False"""
        ...

    @abstractmethod
    def db(self, use_transaction: bool) -> AsyncContextManager[Any]: ...


AbstractAsyncResourceT = TypeVar("AbstractAsyncResourceT", bound=AbstractAsyncResource)


class AbstractSyncResource(Closable, ABC):
    @abstractmethod
    def ping(self) -> bool:
        """健康检查，返回True/False"""
        ...

    @abstractmethod
    def db(self, use_transaction: bool) -> AbstractContextManager[Any]: ...


AbstractSyncResourceT = TypeVar("AbstractSyncResourceT", bound=AbstractSyncResource)
