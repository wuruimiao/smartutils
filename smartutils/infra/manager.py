import functools
import traceback
from typing import Dict, Callable, Any, Awaitable, Generic

from smartutils.call import call_hook
from smartutils.config.const import ConfKey
from smartutils.ctx import ContextVarManager
from smartutils.infra.abstract import T
from smartutils.log import logger


class ContextResourceManager(Generic[T]):
    def __init__(
            self, resources: Dict[str, T], context_var_name: str,
            success: Callable[..., Any] = None,
            fail: Callable[..., Any] = None,
    ):
        self._context_var_name = context_var_name
        self._resources = resources
        self._success = success
        self._fail = fail

    def use(self, key: str = ConfKey.GROUP_DEFAULT):
        def decorator(func: Callable[..., Awaitable[Any]]):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if key not in self._resources:
                    raise RuntimeError(f"No resource found for key: {key}")

                resource = self._resources[key]
                async with resource.session() as session:
                    with ContextVarManager.use(self._context_var_name, session):
                        try:
                            result = await func(*args, **kwargs)
                            await call_hook(self._success, session)
                            return result
                        except Exception as e:
                            await call_hook(self._fail, session)
                            logger.error(f'{key} use err: {traceback.format_exc()}')
                            raise RuntimeError(f'{key} use err') from e

            return wrapper

        return decorator

    def curr(self):
        return ContextVarManager.get(self._context_var_name)

    def client(self, key: str = ConfKey.GROUP_DEFAULT) -> T:
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
