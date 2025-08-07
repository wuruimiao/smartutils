from abc import ABC, abstractmethod
from typing import Iterator, Optional, TypeVar

from smartutils.design._class import MyBase
from smartutils.design.abstract import (
    AsyncClosableProtocol,
    ClosableProtocol,
    IterableProtocol,
)
from smartutils.error.sys import LibraryUsageError

T = TypeVar("T")


class _AbstractContainerBase(MyBase, ABC, IterableProtocol[T]):
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
    def __contains__(self, item: T) -> bool:
        """判断元素是否在容器中"""
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """返回一个迭代器，用于遍历所有元素"""
        ...

    @abstractmethod
    def __len__(self) -> int:
        """返回容器中的元素数量"""
        ...

    def empty(self) -> bool:
        """容器是否为空"""
        return len(self) == 0


class AbstractContainer(_AbstractContainerBase[T], ClosableProtocol):
    @abstractmethod
    def put(self, value: T):
        """
        :param value: 任意对象，只要其可正确哈希。
        """
        ...

    @abstractmethod
    def get(self) -> Optional[T]:
        """
        弹出元素（即value），若无元素则返回None。
        """
        ...

    @abstractmethod
    def close(self):
        """
        关闭容器，容器内元素的关闭应由外部处理
        """
        ...

    @abstractmethod
    def remove(self, value: T) -> Optional[T]:
        """
        删除一个指定value的元素。若存在多个相同value，只删除其中一个。若未找到，返回None。
        """
        ...

    def __enter__(self):
        self.check_closed()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AbstractAsyncContainer(_AbstractContainerBase[T], AsyncClosableProtocol):
    @abstractmethod
    async def put(self, value: T):
        """
        :param value: 任意对象，只要其可正确哈希。
        """
        ...

    @abstractmethod
    async def get(self) -> Optional[T]:
        """
        弹出元素（即value），若无元素则返回None。
        """
        ...

    @abstractmethod
    async def close(self):
        """
        关闭容器，容器内元素的关闭应由外部处理
        """
        ...

    @abstractmethod
    async def remove(self, value: T) -> Optional[T]:
        """
        删除一个指定value的元素。若存在多个相同value，只删除其中一个。若未找到，返回None。
        """
        ...

    async def __aenter__(self):
        self.check_closed()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
