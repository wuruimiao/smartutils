import contextvars
import sys
from contextlib import contextmanager
from typing import Any, Dict

from smartutils.ctx.const import CTXKey
from smartutils.call import exit_on_fail
from smartutils.log import logger
from smartutils.ret.exc import LibraryUsageError

__all__ = ["CTXVarManager"]


class CTXVarManager:
    _vars: Dict[str, contextvars.ContextVar] = {}

    @classmethod
    def _ensure_registered(cls, key: CTXKey):
        if key not in cls._vars:
            msg = f"ContextVarManager must call CTXVarManager.register({key})first"
            logger.error(msg)
            raise LibraryUsageError(msg)

    @classmethod
    def reset_registered(cls):
        pass

    @classmethod
    def _set(cls, key: CTXKey, value: Any):
        cls._ensure_registered(key)
        return cls._vars[key].set(value)  # 返回 token

    @classmethod
    def _reset(cls, key: CTXKey, token: contextvars.Token):
        cls._ensure_registered(key)
        cls._vars[key].reset(token)

    @classmethod
    @contextmanager
    def use(cls, key: CTXKey, value: Any):
        cls._ensure_registered(key)
        token = cls._set(key, value)
        try:
            yield
        finally:
            cls._reset(key, token)

    @classmethod
    def get(cls, key: CTXKey, default: Any = None) -> Any:
        cls._ensure_registered(key)
        try:
            var = cls._vars[key]
            return var.get()
        except LookupError as e:
            if default is not None:
                return default

            msg = f"ContextVarManager must call CTXVarManager.use() {key} first."
            logger.error(msg)
            raise LibraryUsageError(msg)

    @classmethod
    def register(cls, key: CTXKey):
        def decorator(obj):
            if key in cls._vars:
                logger.error("ContextVarManager key {key} already registered.", key=key)
                exit_on_fail()
            cls._vars[key] = contextvars.ContextVar(key)
            return obj

        return decorator
