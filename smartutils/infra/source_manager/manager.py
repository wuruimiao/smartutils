import asyncio
import functools
import threading
from abc import ABC
from typing import Any, Awaitable, Callable, Dict, Generic, Optional, Type

from smartutils.call import call_hook
from smartutils.config.const import ConfKey
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.error.base import BaseError
from smartutils.error.sys import LibraryError, LibraryUsageError, SysError
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
        success: Optional[Callable[..., Any]] = None,
        fail: Optional[Callable[..., Any]] = None,
        error: Optional[Type[SysError]] = None,
    ):
        self._ctx_key: CTXKey = context_var_name
        self._resources = resources
        self._success = success
        self._fail = fail
        self._error = error if error else SysError
        ResourceManagerRegistry.register(self)

    def __str__(self) -> str:
        return f"mgr_{self._ctx_key}"

    # def use(self, key: ConfKey = ConfKey.GROUP_DEFAULT):
    #     def decorator(func: Callable[..., Awaitable[Any]]):
    #         @functools.wraps(func)
    #         async def wrapper(*args, **kwargs):
    #             if key not in self._resources:
    #                 raise LibraryError(f"No resource found for key: {key}")

    #             resource = self._resources[key]
    #             async with resource.session() as session:
    #                 with CTXVarManager.use(self._ctx_key, session):
    #                     try:
    #                         result = await func(*args, **kwargs)
    #                         await call_hook(self._success, session)
    #                         return result
    #                     except BaseError as e:
    #                         raise e
    #                     except Exception as e:
    #                         await call_hook(self._fail, session)
    #                         logger.exception("{key} use fail", key=key)
    #                         raise self._error(f"{key} use fail: {e}") from None

    #         return wrapper

    #     return decorator

    def _build_wrapper(self, func, key):
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
                        logger.exception(f"{key} use fail")
                        raise self._error(f"{key} use fail: {e}") from None

        return wrapper

    def use(self, arg=None):
        # 支持 @mgr.use
        if callable(arg):
            func = arg
            key = ConfKey.GROUP_DEFAULT
            return self._build_wrapper(func, key)

        # 支持 @mgr.use() 或 @mgr.use('key')
        def decorator(func):
            key = arg if arg else ConfKey.GROUP_DEFAULT
            return self._build_wrapper(func, key)

        return decorator

    @property
    def curr(self):
        try:
            return CTXVarManager.get(self._ctx_key)
        except LibraryUsageError:
            raise LibraryUsageError("Must call xxxManager.use(...) first.") from None

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
