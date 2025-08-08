from abc import ABC, abstractmethod
from functools import total_ordering
from typing import Callable, List, Optional, Protocol, TypeVar, runtime_checkable

from smartutils.error.sys import ContainerClosedError

__all__ = [
    "AbstractComparable",
    "ClosableBase",
    "Proxy",
    "ContainerItemProtocol",
    "RemovableProtocol",
    "TAbstractComparable",
]

T = TypeVar("T")


@runtime_checkable
class RemovableProtocol(Protocol[T]):
    """
    支持 remove 方法的鸭子类型协议。
    实现了 remove(self, value) 的对象，都认为符合该协议。
    通用于自定义容器、缓存、池等对象能力约束。
    """

    def remove(self, item: T) -> Optional[T]:
        """
        移除一个元素 item，返回被移除的对象或 None。
        """
        ...


class ClosableBase:
    """
    通用可关闭资源基类，封装关闭状态管理逻辑。
    子类可复用 closed 属性与 _set_closed() 方法，保证资源安全幂等关闭。
    """

    def __init__(self, *args, **kwargs) -> None:
        self._closed: bool = False  # 内部受保护成员，记录关闭状态
        super().__init__(*args, **kwargs)

    @property
    def closed(self) -> bool:
        """
        外部只读属性，表示对象是否已关闭。
        """
        return self._closed

    def raise_for_closed(self) -> None:
        if self.closed:
            raise ContainerClosedError()

    def _set_closed(self):
        """
        标记当前对象为已关闭，供 close 相关资源时调用。
        """
        self._closed = True


@total_ordering
class AbstractComparable(ABC):
    """
    可比较对象抽象基类，实现 __eq__ 和 __lt__ 即可自动推导全部大小比较方法。
    子类需继承并实现 __eq__ 和 __lt__。
    """

    @abstractmethod
    def __eq__(self, other) -> bool:
        """
        判断对象是否相等
        """
        ...

    @abstractmethod
    def __lt__(self, other) -> bool:
        """
        判断对象小于 another
        """
        ...


# 用于泛型约束“可比较对象”的 TypeVar
TAbstractComparable = TypeVar("TAbstractComparable", bound=AbstractComparable)


@runtime_checkable
class ContainerItemProtocol(Protocol):
    def before_put(self): ...

    def after_get(self): ...


class Proxy:
    """
    工具类，批量生成方法代理，将方法调用转发至 self._proxy 的同名方法。
    适用于组合/适配器等设计模式，便于解耦。
    """

    @classmethod
    def _gen_method(cls, name: str) -> Callable:
        """
        生成一个将调用转发至 self._proxy.name 的方法
        """

        def method(self, *args, **kwargs):
            return getattr(self._proxy, name)(*args, **kwargs)

        return method

    @classmethod
    def method(cls, the_cls: type, methods: List[str]):
        """
        批量为 the_cls 类增加方法，将指定方法列表的方法全部代理到 self._proxy 对象上。
        仅实现行为代理，不影响类型提示。
        """
        for _name in methods:
            setattr(the_cls, _name, cls._gen_method(_name))
