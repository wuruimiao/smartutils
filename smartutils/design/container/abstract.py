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
    """
    所有容器类型的抽象基类。

    说明：
        - 线程/协程安全性由ConditionProtocol实现。
        - 容器关闭状态可安全查询，不影响复用性、可扩展性。
        - 遵循开闭原则：修改父类不会影响子容器的扩展。
    """

    def __init__(self, *args, **kwargs) -> None:
        self._closed: bool = False
        super().__init__(*args, **kwargs)

    def check_closed(self) -> None:
        """
        检查容器是否已关闭，是则抛出异常。建议所有修改操作前调用。
        """
        if self._closed:
            raise LibraryUsageError(f"{self.name} closed, no operations allowed.")

    def _set_closed(self) -> None:
        """
        标记为已关闭。避免多次关闭副作用。
        """
        self._closed = True

    @property
    def closed(self) -> bool:
        """
        容器是否已关闭。
        """
        return self._closed

    @abstractmethod
    def __contains__(self, item: T) -> bool:
        """
        判断元素是否在容器中。

        参数:
            item (T): 要查找的元素。

        返回:
            bool: 是否包含。
        """
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """
        获取元素迭代器。

        返回:
            Iterator[T]: 元素迭代器。
        """
        ...

    @abstractmethod
    def __len__(self) -> int:
        """
        获取容器内元素数量。

        返回:
            int: 容器内元素数量。
        """
        ...

    def empty(self) -> bool:
        """
        判断容器是否为空。

        返回:
            bool: 是否为空。
        """
        return len(self) == 0


class AbstractContainer(_AbstractContainerBase[T], ClosableProtocol):
    """
    同步容器抽象类。

    提供 put、get、remove、close 等典型接口，不负责并发安全。
    """

    @abstractmethod
    def put(self, value: T) -> None:
        """
        插入元素。

        参数:
            value (T): 任意可被哈希的对象。
        """
        ...

    @abstractmethod
    def get(self) -> Optional[T]:
        """
        弹出元素（先进先出/后进先出由具体实现决定）。若无元素返回 None。

        返回:
            Optional[T]: 取出的元素，或无元素返回 None。
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """
        关闭容器。内部调用 _set_closed，确保状态一致。子类应先释放资源再调用 super().close()。
        """
        self._set_closed()

    @abstractmethod
    def remove(self, value: T) -> Optional[T]:
        """
        删除指定 value 的一个元素（支持有重复时只删一个）。未找到则返回 None。

        参数:
            value (T): 要删除的元素。

        返回:
            Optional[T]: 删除的元素，未找到返回 None。
        """
        ...

    def __enter__(self):
        self.check_closed()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 建议子类重写 close 时始终调用 super().close()
        self.close()


class AbstractAsyncContainer(_AbstractContainerBase[T], AsyncClosableProtocol):
    """
    异步容器抽象类。接口定义全部为协程函数。
    """

    @abstractmethod
    async def put(self, value: T) -> None:
        """
        异步插入元素。

        参数:
            value (T): 任意可被哈希的对象。
        """
        ...

    @abstractmethod
    async def get(self) -> Optional[T]:
        """
        异步弹出元素。若无元素返回 None。

        返回:
            Optional[T]: 取出的元素，或无元素返回 None。
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """
        异步关闭容器。子类应先释放资源再调用 super().close()。
        """
        self._set_closed()

    @abstractmethod
    async def remove(self, value: T) -> Optional[T]:
        """
        异步删除指定元素，若有重复仅删一个。未找到返回 None。

        参数:
            value (T): 要删除的元素。

        返回:
            Optional[T]: 删除的元素，未找到返回 None。
        """
        ...

    async def __aenter__(self):
        self.check_closed()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
