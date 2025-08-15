from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

from smartutils.design.abstract.common import ClosableBase

__all__ = [
    "AbstractClosable",
    "ClosableProtocol",
    "HealthCheckProtocol",
    "TClosable",
    "THealthCheck",
]

T = TypeVar("T")


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
