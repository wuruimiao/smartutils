from collections import OrderedDict
from typing import Dict, TypeVar, Generic, Tuple, final
from smartutils.error.sys_err import LibraryError, LibraryUsageError


K = TypeVar('K')
V = TypeVar('V')


class BaseFactory(Generic[K, V]):
    _registry: Dict[K, Tuple[int, V]] = {}

    def __init_subclass__(cls):
        cls._registry = {}

    @classmethod
    def register(cls, key: K, only_register_once: bool = True, order: int = 0):
        """
        order越大，生效顺序越靠后
        """
        def decorator(func_or_obj: V):
            if only_register_once and key in cls._registry:
                raise LibraryError(f"{cls.__name__} key {key} already registered.")
            cls._registry[key] = (order, func_or_obj)
            return func_or_obj

        return decorator

    @classmethod
    def get(cls, key: K) -> V:
        if key not in cls._registry:
            raise LibraryUsageError(f"{cls.__name__} key {key} not registered.")
        return cls._registry[key][1]

    @classmethod
    @final
    def all(cls) -> Dict[K, V]:
        items = sorted(cls._registry.items(), key=lambda item: (item[1][0], item[0]))
        return OrderedDict((k, v) for k, (order, v) in items)

    @classmethod
    @final
    def reset(cls):
        cls._registry.clear()
