import contextvars
from contextlib import contextmanager
from typing import Any

from smartutils.ctx.const import CTXKey
from smartutils.design import BaseFactory
from smartutils.error.sys import LibraryUsageError

__all__ = ["CTXVarManager"]


class CTXVarManager(BaseFactory[CTXKey, contextvars.ContextVar]):
    @classmethod
    @contextmanager
    def use(cls, key: CTXKey, value: Any):
        var = super(CTXVarManager, cls).get(key)
        token = var.set(value)
        try:
            yield
        finally:
            var.reset(token)

    @classmethod
    def get(cls, key: CTXKey, default: Any = None) -> Any:
        var = super(CTXVarManager, cls).get(key)
        try:
            return var.get()
        except LookupError as e:
            if default is not None:
                return default

            raise LibraryUsageError(f"Must call CTXVarManager.use({key}) first.") from None

    @classmethod
    def register(cls, key: CTXKey, **kwargs):
        def decorator(obj):
            super(CTXVarManager, cls).register(key, **kwargs)(contextvars.ContextVar(key))
            return obj

        return decorator
