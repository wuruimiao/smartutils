from abc import ABC, abstractmethod
from typing import Optional, Protocol, TypeVar, runtime_checkable

from smartutils.design.abstract.common import ClosableBase

__all__ = [
    "AbstractClosable",
    "ClosableProtocol",
    "HealthCheckProtocol",
    "QueueProtocol",
    "TClosable",
    "THealthCheck",
]

T = TypeVar("T")


@runtime_checkable
class QueueProtocol(Protocol[T]):
    """
    通用队列协议，描述支持 put/get/empty/full 方法的泛型队列类型（鸭子类型）。
    使用 @runtime_checkable 允许 isinstance 检查。
    T: 队列中元素类型。
    """

    def put(self, item: T) -> None: ...

    def get(self) -> Optional[T]: ...

    def empty(self) -> bool: ...

    def full(self) -> bool: ...


class AbstractClosable(ClosableBase, ABC):
    """
    具备可关闭（close）行为的抽象基类，便于资源类的继承和状态管理。
    继承自 ClosableBase，建议子类实现资源释放及关闭状态标记。
    """

    @abstractmethod
    def close(self) -> None:
        """
        关闭对象，释放相关资源。子类实现时应调用 super().close() 保证关闭状态被正确记录，避免重复释放。
        """
        self._set_closed()


@runtime_checkable
class ClosableProtocol(Protocol):
    """
    可关闭资源对象协议。实现 close() 方法即可与此 Duck Typing 协议兼容。
    适合泛型、池、临时文件等场景被类型约束或静态检查。
    """

    def close(self) -> None: ...


# 可关闭资源的泛型 TypeVar，约束类型需实现 ClosableProtocol
TClosable = TypeVar("TClosable", bound=ClosableProtocol)


@runtime_checkable
class HealthCheckProtocol(Protocol):
    """
    健康检查能力协议。实现 ping() 方法，用于健康/存活性探测/上报等场景，返回资源健康状态。
    """

    def ping(self) -> bool: ...


# 具备健康检查能力的泛型 TypeVar，约束类型需实现 HealthCheckProtocol
THealthCheck = TypeVar("THealthCheck", bound=HealthCheckProtocol)
