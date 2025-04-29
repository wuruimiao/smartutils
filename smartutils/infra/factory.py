from typing import Callable, Any, Dict


class InfraFactory:
    _registry: Dict[str, Callable[[Any], Any]] = {}

    @classmethod
    def register(cls, key: str):
        def decorator(func: Callable[[Any], Any]):
            cls._registry[key] = func
            return func

        return decorator

    @classmethod
    def get(cls, key: str):
        return cls._registry.get(key)

    @classmethod
    def all(cls):
        return cls._registry

    @classmethod
    def reset(cls):
        cls._registry.clear()
