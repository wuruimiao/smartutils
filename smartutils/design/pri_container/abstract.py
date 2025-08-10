from dataclasses import dataclass
from typing import Optional, Protocol, TypeVar, runtime_checkable

import ulid

from smartutils.design._class import MyBase
from smartutils.design.abstract.common import ContainerItemProtocol

T = TypeVar("T")


@runtime_checkable
class PriContainerProtocol(Protocol[T]):
    """
    不要求TSortable，容器实现可能不直接比较实例大小，交由子类决定
    """

    def put(self, item: T) -> None: ...

    def get_min(self) -> Optional[T]:
        """
        弹出并返回优先级最小的元素（即value），若无元素则返回None。
        """
        ...

    def get_max(self) -> Optional[T]:
        """
        弹出并返回优先级最大的元素（value）。无元素返回None。
        """
        ...


class PriContainerItemBase(MyBase, ContainerItemProtocol):
    def __init__(self, value) -> None:
        self.value = value
        self._priority = 0
        # 在Manager模式下，序列化反序列化后，内存地址不同，默认id(self)无法判等
        # 需要唯一ID
        self._inst_id = str(ulid.new())
        super().__init__()

    @property
    def inst_id(self) -> str:
        return self._inst_id

    @property
    def priority(self):
        return self._priority

    def __repr__(self) -> str:
        return f"{self.name}<{self.inst_id}>"


TPriContainerItem = TypeVar("TPriContainerItem", bound=PriContainerItemBase)


@dataclass
class InstPri:
    priority: int
    inst_id: str
