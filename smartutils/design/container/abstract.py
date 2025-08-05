from typing import Optional, Protocol, TypeVar, Union, runtime_checkable

from smartutils.design._class import MyBase
from smartutils.error.sys import LibraryUsageError

T = TypeVar("T")


class ContainerBase(MyBase):
    def __init__(self, *args, **kwargs) -> None:
        self._closed: bool = False
        super().__init__(*args, **kwargs)

    def check_closed(self):
        if self._closed:
            raise LibraryUsageError(f"{self.name} closed, no operations allowed.")

    def set_closed(self) -> None:
        """
        关闭容器
        """
        self._closed = True


@runtime_checkable
class PriContainer(Protocol[T]):  # type: ignore
    """
    优先级容器的通用抽象协议。所有外部增删查改均只操作value实例，不暴露任何内部存储结构。
    设计目标：任何put、pop、remove等操作后，value实例的inst_id全生命周期内保持不变。
    子类实现内部应以PriorityItemWrap为唯一挂载元素。
    """

    def put(self, value: T, priority: Union[float, int]):
        """
        :param value: 任意对象，只要其可正确哈希。
        :param priority: 优先级。数值越小，优先级越高。
        """
        ...

    def pop_min(self) -> Optional[T]:
        """
        弹出并返回优先级最小的元素（即value），若无元素则返回None。
        """
        ...

    def pop_max(self) -> Optional[T]:
        """
        弹出并返回优先级最大的元素（value）。无元素返回None。
        """
        ...

    def remove(self, value: T) -> Optional[T]:
        """
        删除一个指定value的元素。若存在多个相同value，只删除其中一个。若未找到，返回None。
        """
        ...

    def __len__(self) -> int: ...
