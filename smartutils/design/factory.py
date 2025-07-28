from collections import OrderedDict
from typing import Callable, Generic, Tuple, TypeVar, final

from smartutils.error.sys import LibraryError, LibraryUsageError

K = TypeVar("K")
V = TypeVar("V")


class BaseFactory(Generic[K, V]):
    _registry_value: OrderedDict[K, V] = OrderedDict()
    _registry_order: dict[K, int] = {}

    def __init_subclass__(cls):
        cls._registry_value = OrderedDict()
        cls._registry_order = {}

    @classmethod
    def _with_order(cls, key: K, value: V, order: int):
        cls._registry_order[key] = order
        # 有序插入
        items = list(cls._registry_value.items())
        for idx, (exist_key, _) in enumerate(items):
            exist_order = cls._registry_order.get(exist_key, 0)
            if order <= exist_order:
                break
        else:
            # 没有break
            idx = len(items)
        items.insert(idx, (key, value))
        cls._registry_value = OrderedDict(items)

    @classmethod
    def register(
        cls, key: K, only_register_once: bool = True, order: int = 0
    ) -> Callable[[V], V]:
        """
        order越大，生效顺序越靠后；
        注意：类装饰器的注册/副作用”只会在首次 import 时发生，之后重新实例化并不会自动重新注册

        Args:
            key (K): key类
            only_register_once (bool, optional): 只能注册一次. Defaults to True.
            order (int, optional): 生效顺序. Defaults to 0.
        """

        def decorator(func_or_obj: V):
            if only_register_once and key in cls._registry_value:
                raise LibraryError(f"{cls.__name__} key {key} already registered.")

            cls._with_order(key, func_or_obj, order)
            return func_or_obj

        return decorator

    @classmethod
    def get(cls, key: K) -> V:
        if key not in cls._registry_value:
            raise LibraryUsageError(f"{cls.__name__} key {key} not registered.")
        return cls._registry_value[key]

    @classmethod
    @final
    def all(cls) -> Tuple[Tuple[K, V], ...]:
        return tuple(cls._registry_value.items())

    @classmethod
    @final
    def reset(cls):
        cls._registry_value.clear()
        cls._registry_order.clear()
