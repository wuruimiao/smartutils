from typing import Optional, Protocol, TypeVar, Union, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class PriContainerProtocol(Protocol[T]):
    """
    优先级容器的通用抽象协议。所有外部增删查改均只操作value实例，不暴露任何内部存储结构。
    设计目标：任何put、pop、remove等操作后，value实例的inst_id全生命周期内保持不变。
    子类实现内部应以PriorityItemWrap为唯一挂载元素。
    """

    def push(self, value: T, priority: Union[float, int]):
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
