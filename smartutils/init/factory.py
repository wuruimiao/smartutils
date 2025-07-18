from typing import Any, Callable, Tuple

from smartutils.config.const import ConfKey
from smartutils.design import BaseFactory

__all__ = ["InfraFactory"]


class InfraFactory(BaseFactory[ConfKey, Tuple[Callable[[Any], Any], bool]]):
    @classmethod
    def register(cls, key: ConfKey, need_conf: bool = True, **kwargs):  # type: ignore
        def decorator(func: Callable[[Any], Any]):
            super(InfraFactory, cls).register(key, **kwargs)((func, need_conf))
            return func

        return decorator
