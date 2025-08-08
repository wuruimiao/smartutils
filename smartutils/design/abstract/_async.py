from abc import ABC, abstractmethod
from typing import Optional, Protocol, TypeVar, runtime_checkable

from smartutils.design.abstract.common import ClosableBase

T = TypeVar("T")


@runtime_checkable
class AsyncQueueProtocol(Protocol[T]):
    """
    通用异步队列协议，描述支持 async put/get 方法并可判空/判满的队列。
    泛型参数T指定队列中存储的元素类型。
    便于类型提示和鸭子类型约束，支持 isinstance 检查。
    """

    async def put(self, item: T) -> None: ...

    async def get(self) -> Optional[T]: ...

    def empty(self) -> bool: ...

    def full(self) -> bool: ...


class AbstractAsyncClosable(ClosableBase, ABC):
    """
    抽象异步可关闭对象基类，提供资源关闭标准接口。
    子类应实现 async close 方法，并在关闭后设置关闭状态，避免资源重复释放。
    """

    @abstractmethod
    async def close(self) -> None:
        """
        异步关闭对象，释放相关资源。
        子类可在此方法中释放资源并设置 super().close() 标记已关闭状态。
        """
        self._set_closed()


@runtime_checkable
class AsyncClosableProtocol(Protocol):
    """
    Duck typing 异步可关闭协议。只要实现 async close 方法即可认为符合本协议。
    支持泛型约束与静态/运行时检查。
    """

    async def close(self) -> None: ...


# 泛型，可约束为“具备 async close 能力”的类
TAsyncClosable = TypeVar("TAsyncClosable", bound=AsyncClosableProtocol)


@runtime_checkable
class AsyncHealthCheckProtocol(Protocol):
    """
    Duck typing 异步健康检查协议。实现 async ping 方法即可与之兼容。
    适合数据库、远程连接等异步健康检测场景。
    """

    async def ping(self) -> bool: ...


# 泛型，可约束为“具备 async ping 能力”的类
TAsyncHealthCheck = TypeVar("TAsyncHealthCheck", bound=AsyncHealthCheckProtocol)
