from typing import Callable, Any, Tuple

from smartutils.design import BaseFactory

__all__ = ["InfraFactory"]


class InfraFactory(BaseFactory[str, Tuple[Callable[[Any], Any], bool]]):
    @classmethod
    def register(cls, key: str, need_conf: bool = True):
        def decorator(func: Callable[[Any], Any]):
            super(InfraFactory, cls).register(key)((func, need_conf))
            return func

        return decorator
