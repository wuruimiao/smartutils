from typing import Dict, TypeVar, Generic, final

from smartutils.log import logger
from smartutils.call import exit_on_fail
from smartutils.error.sys_err import LibraryError

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
                logger.error("{name} key {key} already registered.", name=cls.__name__, key=key)
                exit_on_fail()
            cls._registry[key] = func_or_obj
            return func_or_obj

        return decorator

    @classmethod
    def get(cls, key: K) -> V:
        if key not in cls._registry:
            msg = f"{cls.__name__} key {key} not registered."
            logger.error(msg)
            raise LibraryError(msg)
        return cls._registry[key]

    @classmethod
    @final
    def all(cls) -> Dict[K, V]:
        return dict(cls._registry)

    @classmethod
    @final
    def reset(cls):
        cls._registry.clear()