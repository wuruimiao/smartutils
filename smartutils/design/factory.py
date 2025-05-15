from collections import OrderedDict
from typing import TypeVar, Generic, Tuple, final, Iterator

from smartutils.error.sys import LibraryError, LibraryUsageError

K = TypeVar('K')
V = TypeVar('V')


class BaseFactory(Generic[K, V]):
    _registry: OrderedDict[K, Tuple[int, V]] = OrderedDict()

    def __init_subclass__(cls):
        cls._registry = OrderedDict()

    @classmethod
    def register(cls, key: K, only_register_once: bool = True, order: int = 0):
        """
        order越大，生效顺序越靠后
        """

        def decorator(func_or_obj: V):
            if only_register_once and key in cls._registry:
                raise LibraryError(f"{cls.__name__} key {key} already registered.")
            items = list(cls._registry.items())
            for idx, (exist_key, (exist_order, _)) in enumerate(items):
                if order < exist_order:
                    break
            else:
                idx = len(items)
            items.insert(idx, (key, (order, func_or_obj)))
            cls._registry = OrderedDict(items)
            return func_or_obj

        return decorator

    @classmethod
    def get(cls, key: K) -> V:
        if key not in cls._registry:
            raise LibraryUsageError(f"{cls.__name__} key {key} not registered.")
        return cls._registry[key][1]

    @classmethod
    @final
    def all(cls) -> Iterator[Tuple[K, V]]:
        return ((k, v) for k, (order, v) in cls._registry.items())

    @classmethod
    @final
    def reset(cls):
        cls._registry.clear()
