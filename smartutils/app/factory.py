from typing import List, Awaitable
from typing import Type, Callable, Dict, Any

from smartutils.error.base import BaseError
from smartutils.app.const import AppKey
from smartutils.log import logger
from smartutils.call import exit_on_fail

__all__ = ["AppHook", "JsonRespFactory", "ExcJsonResp", "ExcFactory"]


class AppHook:
    """
    通用生命周期钩子注册器，支持 on_startup/on_shutdown，
    钩子函数参数类型不做限定。
    """

    _startup_hooks: List[Callable[..., Awaitable[None]]] = []
    _shutdown_hooks: List[Callable[..., Awaitable[None]]] = []

    @classmethod
    def on_startup(
            cls, func: Callable[..., Awaitable[None]]
    ) -> Callable[..., Awaitable[None]]:
        """注册服务启动前的钩子函数（参数不限）"""
        cls._startup_hooks.append(func)
        return func

    @classmethod
    def on_shutdown(
            cls, func: Callable[..., Awaitable[None]]
    ) -> Callable[..., Awaitable[None]]:
        """注册服务关闭前的钩子函数（参数不限）"""
        cls._shutdown_hooks.append(func)
        return func

    @classmethod
    async def call_startup(cls, *args, **kwargs):
        for hook in cls._startup_hooks:
            await hook(*args, **kwargs)

    @classmethod
    async def call_shutdown(cls, *args, **kwargs):
        for hook in cls._shutdown_hooks:
            await hook(*args, **kwargs)


class ExcFactory:
    _mapping: Dict[Type[BaseException], Callable[[BaseException], BaseError]] = {}

    @classmethod
    def register(cls, ext_exc_type: Type[BaseException]):
        def decorator(func: Callable[[BaseException], BaseError]):
            if ext_exc_type in cls._mapping:
                logger.error("ExcFactory key {key} already registered.", key=ext_exc_type)
                exit_on_fail()
            cls._mapping[ext_exc_type] = func
            return func

        return decorator

    @classmethod
    def map(cls, exc: BaseException) -> BaseError:
        for ext_type, handler in cls._mapping.items():
            if isinstance(exc, ext_type):
                return handler(exc)
        from smartutils.error.sys_err import SysError
        return SysError(detail=str(exc))


class JsonRespFactory:
    _mapping: Dict[AppKey, Callable[[BaseError], Any]] = {}

    @classmethod
    def register(cls, key: AppKey):
        def decorator(func: Callable[[BaseError], Any]):
            if key in cls._mapping:
                logger.error("JsonRespFactory key {key} already registered.", key=key)
                exit_on_fail()
            cls._mapping[key] = func
            return func

        return decorator

    @classmethod
    def get(cls, key: AppKey) -> Callable[[BaseError], Any]:
        return cls._mapping[key]


class ExcJsonResp:
    @classmethod
    def handle(cls, exc: BaseException, key: AppKey) -> Any:
        mapped_exc = ExcFactory.map(exc)
        resp_fn = JsonRespFactory.get(key)
        return resp_fn(mapped_exc)
