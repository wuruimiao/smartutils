from typing import Callable, Any, Dict, Tuple

__all__ = ["InfraFactory"]


class InfraFactory:
    _registry: Dict[str, Tuple[Callable[[Any], Any], bool]] = {}

    @classmethod
    def register(cls, key: str, need_conf: bool = True):
        def decorator(func: Callable[[Any], Any]):
            cls._registry[key] = (func, need_conf)
            return func

        return decorator

    @classmethod
    def get(cls, key: str):
        return cls._registry.get(key)

    @classmethod
    def all(cls) -> Dict[str, Tuple[Callable[[Any], Any], bool]]:
        return cls._registry

    @classmethod
    def reset(cls):
        cls._registry.clear()
