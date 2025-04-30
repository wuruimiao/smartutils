import contextvars
from typing import Any, Dict, Callable
from contextlib import contextmanager
from smartutils.log import logger
from smartutils.ctx.const import CTXKey
import functools


class CTXVarManager:
    _vars: Dict[str, contextvars.ContextVar] = {}

    @classmethod
    def _ensure_registered(cls, key: CTXKey):
        if key not in cls._vars:
            msg = f"ContextVarManager error: key {key} not registered"
            logger.error(msg)
            raise RuntimeError(msg)

    @classmethod
    def reset_registered(cls):
        pass

    @classmethod
    def _register(cls, key: CTXKey):
        if key in cls._vars:
            raise ValueError(
                f"ContextVarManager register error: key {key} already registered"
            )
        cls._vars[key] = contextvars.ContextVar(key)

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

            logger.exception(f"ContextVarManager get error")
            raise RuntimeError(f"ContextVarManager get error: {e}")

    @classmethod
    def register(cls, key: CTXKey):
        def decorator(obj):
            cls._register(key)
            return obj

        return decorator
