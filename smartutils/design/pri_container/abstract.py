from typing import Optional, Protocol, TypeVar, runtime_checkable

from smartutils.design.abstract.common import (
    AbstractComparable,
    ContainerItemProtocol,
    TAbstractComparable,
)


@runtime_checkable
class PriContainerProtocol(Protocol[TAbstractComparable]):
    def put(self, item: TAbstractComparable) -> None: ...

    def get_min(self) -> Optional[TAbstractComparable]:
        """
        弹出并返回优先级最小的元素（即value），若无元素则返回None。
        """
        ...

    def get_max(self) -> Optional[TAbstractComparable]:
        """
        弹出并返回优先级最大的元素（value）。无元素返回None。
        """
        ...


class PriContainerItemBase(AbstractComparable, ContainerItemProtocol):
    def __init__(self, value) -> None:
        self.value = value
        self._priority = 0
        super().__init__()

    def __eq__(self, other) -> bool:
        return self._priority == other._priority

    def __lt__(self, other) -> bool:
        return self._priority < other._priority


TPriContainerItem = TypeVar("TPriContainerItem", bound=PriContainerItemBase)
