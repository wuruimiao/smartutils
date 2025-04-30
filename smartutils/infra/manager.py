import asyncio
import functools
import threading
import traceback
from typing import Dict, Callable, Any, Awaitable, Generic

from smartutils.call import call_hook
from smartutils.config.const import ConfKeys, ConfKey
from smartutils.ctx import CTXVarManager, CTXKey
from smartutils.infra.abstract import T
from smartutils.log import logger

__all__ = [
    "ResourceManagerRegistry",
    "ContextResourceManager",
]


class ResourceManagerRegistry:
    _instances = []
    _lock = threading.Lock()

    @classmethod
    def register(cls, instance):
        with cls._lock:
            cls._instances.append(instance)

    @classmethod
    def get_all(cls):
        with cls._lock:
            return list(cls._instances)

    @classmethod
    async def close_all(cls):
        await asyncio.gather(
            *(mgr.close() for mgr in ResourceManagerRegistry.get_all())
        )


class ContextResourceManager(Generic[T]):
    def __init__(
        self,
        resources: Dict[ConfKey, T],
        context_var_name: CTXKey,
        success: Callable[..., Any] = None,
        fail: Callable[..., Any] = None,
    ):
        self._ctx_key: CTXKey = context_var_name
        self._resources = resources
        self._success = success
        self._fail = fail
        ResourceManagerRegistry.register(self)

    def __str__(self) -> str:
        return f"mgr_{self._ctx_key}"

    def use(self, key: ConfKey = ConfKeys.GROUP_DEFAULT):
        def decorator(func: Callable[..., Awaitable[Any]]):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if key not in self._resources:
                    raise RuntimeError(f"No resource found for key: {key}")

                resource = self._resources[key]
                async with resource.session() as session:
                    with CTXVarManager.use(self._ctx_key, session):
                        try:
                            result = await func(*args, **kwargs)
                            await call_hook(self._success, session)
                            return result
                        except Exception as e:
                            await call_hook(self._fail, session)
                            logger.exception(f"{key} use fail")
                            raise RuntimeError(f"{key} use fail") from e

            return wrapper

        return decorator

    def curr(self):
        return CTXVarManager.get(self._ctx_key)

    def client(self, key: ConfKey = ConfKeys.GROUP_DEFAULT) -> T:
        if key not in self._resources:
            raise RuntimeError(f"No resource found for key: {key}")
        return self._resources[key]

    async def close(self):
        for key, cli in self._resources.items():
            try:
                await cli.close()
            except: # noqa
                logger.exception(
                    f"ContextResourceManager Failed to close {self} {key}"
                )

    async def health_check(self) -> Dict[str, bool]:
        result = {}
        for key, cli in self._resources.items():
            result[key] = await cli.ping()
        return result
