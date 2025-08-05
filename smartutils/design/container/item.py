import uuid
from typing import Generic, Optional, TypeVar, Union

from smartutils.design._class import MyBase

T = TypeVar("T")


class ContainerItemWrap(Generic[T], MyBase):
    """
    优先级容器内部存储元素，绑定唯一ID、实例对象。
    """

    def __init__(self, *, value: T, inst_id: Optional[str] = None):
        self._inst_id = inst_id or str(uuid.uuid4())
        self._value = value
        self.count = 0

    @property
    def inst_id(self) -> str:
        return self._inst_id

    @property
    def value(self) -> T:
        return self._value

    def __str__(self) -> str:
        return f"<{self.name} id={self.inst_id} cnt={self.count} val={self.value!r}>"


class PriItemWrap(ContainerItemWrap[T]):
    """
    优先级容器的内部数据结构。每个value仅由一个PriorityItemWrap对象包装，保证外部任何操作（如插入、弹出、删除、查找）
    时value与其inst_id不变。inst_id只限内部追踪，外部接口始终只暴露实际的value对象。
    """

    def __init__(
        self,
        *,
        value: T,
        priority: Union[float, int],
        inst_id: Optional[str] = None,
    ):
        super().__init__(value=value, inst_id=inst_id)
        self.priority = priority

    def __str__(self) -> str:
        return f"{super().__str__()} priority={self.priority}"
