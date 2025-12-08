from abc import ABC, abstractmethod
from typing import Callable, Generic, Type

from smartutils.design.factory import BaseFactory, K, MetaT, V


class TypeDispatchBaseFactory(
    Generic[K, V, MetaT], BaseFactory[Type[K], Callable[[K], V], MetaT], ABC
):
    """
    提供了基于类型进行动态分发（类型分派）的注册与调用机制，
    主要用于如下场景：
        - 注册阶段以类型（通常为异常类型）为 key，将处理函数/适配器/工厂方法作为 value
        - 调用阶段输入一个实例（如异常对象），自动找到最匹配的已注册类型，执行其对应处理方法
    设计目的：
        - 适配“异常处理链”、“多类型输入自适应处理函数”等实际工程需求
        - 避免传统工厂 get 方法只能做严格 key-value 查找的不便，增强动态分派能力
        - 保持 BaseFactory 的注册等机制兼容性，又实现类型分派语义

    典型用例：
        class ExcErrorFactory(TypeDispatchFactory[BaseException, str, None]): ...
        @ExcErrorFactory.register(ValueError)
        def _(e: ValueError) -> str: return "msg"
        ExcErrorFactory.dispatch(ValueError())   # => "msg"
    """

    @classmethod
    @abstractmethod
    def v_type(cls) -> Type[V]:
        """
        子类必须实现，返回 value 的标准类型
        """
        ...

    @classmethod
    @abstractmethod
    def default(cls, key: K) -> V:
        """
        子类必须实现，提供默认的处理逻辑
        """
        ...

    @classmethod
    def dispatch(cls, key: K) -> V:
        if isinstance(key, cls.v_type()):
            return key

        for cls_type, handler in cls.all():
            if isinstance(key, cls_type):
                return handler(key)

        return cls.default(key)
