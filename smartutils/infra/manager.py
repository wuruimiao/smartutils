import functools
import logging
import traceback
from contextvars import ContextVar
from typing import Dict, Callable, Any, Awaitable, Generic

from smartutils.config.const import CONF_DEFAULT
from smartutils.infra.abstract import T
from smartutils.call import call_hook

logger = logging.getLogger(__name__)

_CONTEXT_VAR_NAMES = set()


def reset():
    _CONTEXT_VAR_NAMES.clear()


class ContextResourceManager(Generic[T]):
    def __init__(
            self, resources: Dict[str, T], context_var_name: str,
            success: Callable[..., Any] = None,
            fail: Callable[..., Any] = None,
    ):
        if context_var_name in _CONTEXT_VAR_NAMES:
            raise ValueError(f"context_var_name '{context_var_name}' already used in ContextResourceManager")
        _CONTEXT_VAR_NAMES.add(context_var_name)

        self._context_var = ContextVar(context_var_name)
        self._resources = resources
        self._success = success
        self._fail = fail

    def use(self, key: str = CONF_DEFAULT):
        def decorator(func: Callable[..., Awaitable[Any]]):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if key not in self._resources:
                    raise RuntimeError(f"No resource found for key: {key}")

                resource = self._resources[key]
                async with resource.session() as session:
                    token = self._context_var.set(session)
                    try:
                        result = await func(*args, **kwargs)
                        await call_hook(self._success, session)
                        return result
                    except Exception as e:
                        await call_hook(self._fail, session)
                        logger.error(f'{key} use err: {traceback.format_exc()}')
                        raise RuntimeError(f'{key} use err') from e
                    finally:
                        self._context_var.reset(token)

            return wrapper

        return decorator

    def curr(self):
        try:
            return self._context_var.get()
        except LookupError as e:
            logger.error(f'curr db err: {traceback.format_exc()}')
            raise RuntimeError(f'curr err') from e

    def client(self, key: str = CONF_DEFAULT) -> T:
        if key not in self._resources:
            raise RuntimeError(f"No resource found for key: {key}")
        return self._resources[key]

    async def close(self):
        for cli in self._resources.values():
            await cli.close()

    async def health_check(self) -> Dict[str, bool]:
        result = {}
        for key, cli in self._resources.items():
            result[key] = await cli.ping()
        return result
