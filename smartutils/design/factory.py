from typing import Dict, TypeVar, Generic, final

from smartutils.error.sys_err import LibraryError, LibraryUsageError

K = TypeVar('K')
V = TypeVar('V')


class BaseFactory(Generic[K, V]):
    _registry: Dict[K, V] = {}

    def __init_subclass__(cls):
        cls._registry = {}

    @classmethod
    def register(cls, key: K, only_register_once: bool = True):
        def decorator(func_or_obj: V):
            if only_register_once and key in cls._registry:
                raise LibraryError(f"{cls.__name__} key {key} already registered.")
            cls._registry[key] = func_or_obj
            return func_or_obj

        return decorator

    @classmethod
    def get(cls, key: K) -> V:
        if key not in cls._registry:
            raise LibraryUsageError(f"{cls.__name__} key {key} not registered.")
        return cls._registry[key]

    @classmethod
    @final
    def all(cls) -> Dict[K, V]:
        return dict(cls._registry)

    @classmethod
    @final
    def reset(cls):
        cls._registry.clear()
