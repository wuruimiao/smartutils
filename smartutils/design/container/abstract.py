from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from smartutils.design._class import MyBase
from smartutils.error.sys import LibraryUsageError

T = TypeVar("T")


class AbstractContainer(MyBase, ABC, Generic[T]):
    def __init__(self, *args, **kwargs) -> None:
        self._closed: bool = False
        super().__init__(*args, **kwargs)

    def check_closed(self):
        if self._closed:
            raise LibraryUsageError(f"{self.name} closed, no operations allowed.")

    def _set_closed(self) -> None:
        """
        关闭容器
        """
        self._closed = True

    @abstractmethod
    def close(self) -> List[T]:
        """
        关闭容器，容器内元素的关闭应由外部处理
        """
        ...

    def __enter__(self):
        self.check_closed()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AbstractAsyncContainer(MyBase, ABC, Generic[T]):
    def __init__(self, *args, **kwargs) -> None:
        self._closed: bool = False
        super().__init__(*args, **kwargs)

    def check_closed(self):
        if self._closed:
            raise LibraryUsageError(f"{self.name} closed, no operations allowed.")

    def _set_closed(self) -> None:
        """
        关闭容器
        """
        self._closed = True

    @abstractmethod
    async def close(self) -> List[T]:
        """
        关闭容器，容器内元素的关闭应由外部处理
        """
        ...

    async def __aenter__(self):
        self.check_closed()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
