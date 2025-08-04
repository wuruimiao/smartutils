from typing import Optional, Protocol, Tuple, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class AbstractPriorityContainer(Protocol[T]):
    """
    抽象优先级容器的统一接口，方便扩展其他数据结构与算法实现。
    """

    def put(self, priority: int, value: T) -> str:
        """
        插入元素，返回实例ID。
        """
        ...

    def pop_min(self) -> Optional[Tuple[str, T]]:
        """
        O(1)或O(logN)取并删除优先级最小实例。
        """
        ...

    def pop_max(self) -> Optional[Tuple[str, T]]:
        """
        O(1)或O(logN)取并删除优先级最大实例。
        """
        ...

    def remove(self, inst_id: str) -> Optional[T]:
        """
        O(1)或O(logN)按实例ID删除
        """
        ...

    def __len__(self) -> int: ...

    def __contains__(self, inst_id: str) -> bool: ...
