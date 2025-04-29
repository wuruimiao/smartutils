import contextvars
from typing import Any, Dict, Callable
from contextlib import contextmanager
from loguru import logger
import functools


class ContextVarManager:
    _vars: Dict[str, contextvars.ContextVar] = {}

    @classmethod
    def _ensure_registered(cls, key: str):
        if key not in cls._vars:
            logger.error(f"ContextVarManager error: key '{key}' not registered")
            raise RuntimeError(f"ContextVarManager error: key '{key}' not registered")

    @classmethod
    def reset_registered(cls):
        pass

    @classmethod
    def _register(cls, key: str):
        if key in cls._vars:
            raise ValueError(f"ContextVarManager register error: key '{key}' already registered")
        cls._vars[key] = contextvars.ContextVar(key)

    @classmethod
    def _set(cls, key: str, value: Any):
        cls._ensure_registered(key)
        return cls._vars[key].set(value)  # 返回 token

    @classmethod
    def _reset(cls, key: str, token: contextvars.Token):
        cls._ensure_registered(key)
        cls._vars[key].reset(token)

    @classmethod
    @contextmanager
    def use(cls, key: str, value: Any):
        cls._ensure_registered(key)
        token = cls._set(key, value)
        try:
            yield
        finally:
            cls._reset(key, token)

    @classmethod
    def get(cls, key: str) -> Any:
        cls._ensure_registered(key)
        try:
            var = cls._vars[key]
            return var.get()
        except LookupError as e:
            logger.error(f'ContextVarManager get error: {e}')
            raise RuntimeError(f'ContextVarManager get error: {e}')

    @classmethod
    def register(cls, key: str):
        def decorator(func: Callable):
            cls._register(key)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator
