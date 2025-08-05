import uuid
from typing import Optional, Protocol, TypeVar, runtime_checkable

from smartutils.design._class import MyBase


class ContainerItemWrap(MyBase):
    """
    优先级容器内部存储元素，绑定唯一ID、实例对象。
    """

    def __init__(self, *, value: object, inst_id: Optional[str] = None):
        self._inst_id = inst_id or str(uuid.uuid4())
        self._value = value
        self.count = 0

    @property
    def inst_id(self) -> str:
        return self._inst_id

    @property
    def value(self) -> object:
        return self._value

    def __str__(self) -> str:
        return f"<{self.name} id={self.inst_id} cnt={self.count} val={self.value!r}>"


class PriorityItemWrap(ContainerItemWrap):
    """
    优先级容器的内部数据结构。每个value仅由一个PriorityItemWrap对象包装，保证外部任何操作（如插入、弹出、删除、查找）
    时value与其inst_id不变。inst_id只限内部追踪，外部接口始终只暴露实际的value对象。
    """

    def __init__(self, *, value: object, priority: int, inst_id: Optional[str] = None):
        super().__init__(value=value, inst_id=inst_id)
        self.priority = priority

    def __str__(self) -> str:
        return f"{super().__str__()} priority={self.priority}"


PriorityItemWrapT = TypeVar("PriorityItemWrapT", bound=PriorityItemWrap, covariant=True)


@runtime_checkable
class AbstractPriorityContainer(Protocol[PriorityItemWrapT]):
    """
    优先级容器的通用抽象协议。所有外部增删查改均只操作value实例，不暴露任何内部存储结构。
    设计目标：任何put、pop、remove等操作后，value实例的inst_id全生命周期内保持不变。
    子类实现内部应以PriorityItemWrap为唯一挂载元素。
    """

    def put(self, value: object, priority: int):
        """
        :param value: 任意对象，只要其可正确哈希。
        :param priority: 优先级。数值越小，优先级越高。
        """
        ...

    def pop_min(self) -> Optional[object]:
        """
        弹出并返回优先级最小的元素（即value），若无元素则返回None。
        """
        ...

    def pop_max(self) -> Optional[object]:
        """
        弹出并返回优先级最大的元素（value）。无元素返回None。
        """
        ...

    def remove(self, value: object) -> Optional[object]:
        """
        删除一个指定value的元素。若存在多个相同value，只删除其中一个。若未找到，返回None。
        """
        ...

    def clear(self) -> None:
        """
        清空所有元素。
        """
        ...

    def __len__(self) -> int: ...
