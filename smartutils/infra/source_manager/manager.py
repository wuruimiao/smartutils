import asyncio
import functools
import threading
from abc import ABC
from typing import Dict, Callable, Any, Awaitable, Generic, Type

from smartutils.call import call_hook
from smartutils.config.const import ConfKey
from smartutils.ctx import CTXVarManager, CTXKey
from smartutils.error.base import BaseError
from smartutils.error.sys import SysError, LibraryError, LibraryUsageError
from smartutils.infra.source_manager.abstract import T
from smartutils.log import logger

__all__ = ["ResourceManagerRegistry", "CTXResourceManager"]


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


class CTXResourceManager(Generic[T], ABC):
    def __init__(
            self,
            resources: Dict[ConfKey, T],
            context_var_name: CTXKey,
            success: Callable[..., Any] = None,
            fail: Callable[..., Any] = None,
            error: Type[SysError] = None
    ):
        self._ctx_key: CTXKey = context_var_name
        self._resources = resources
        self._success = success
        self._fail = fail
        self._error = error if error else SysError
        ResourceManagerRegistry.register(self)

    def __str__(self) -> str:
        return f"mgr_{self._ctx_key}"

    def use(self, key: ConfKey = ConfKey.GROUP_DEFAULT):
        def decorator(func: Callable[..., Awaitable[Any]]):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if key not in self._resources:
                    raise LibraryError(f"No resource found for key: {key}")

                resource = self._resources[key]
                async with resource.session() as session:
                    with CTXVarManager.use(self._ctx_key, session):
                        try:
                            result = await func(*args, **kwargs)
                            await call_hook(self._success, session)
                            return result
                        except BaseError as e:
                            raise e
                        except Exception as e:
                            await call_hook(self._fail, session)
                            logger.exception("{key} use fail", key=key)
                            raise self._error(f"{key} use fail: {e}") from None

            return wrapper

        return decorator

    @property
    def curr(self):
        try:
            return CTXVarManager.get(self._ctx_key)
        except LibraryUsageError:
            raise LibraryUsageError(f"Must call xxxManager.use(...) first.") from None

    def client(self, key: ConfKey = ConfKey.GROUP_DEFAULT) -> T:
        if key not in self._resources:
            raise LibraryError(f"No resource found for key: {key}")
        return self._resources[key]

    async def close(self):
        for key, cli in self._resources.items():
            try:
                await cli.close()
            except:  # noqa
                logger.exception(
                    "CTXResourceManager Failed to close {self} {key}",
                    self=self,
                    key=key,
                )

    async def health_check(self) -> Dict[str, bool]:
        result = {}
        for key, cli in self._resources.items():
            result[key] = await cli.ping()
        return result
