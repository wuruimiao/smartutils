from typing import List, Awaitable, Type, Callable, Any

from smartutils.app.const import AppKey
from smartutils.design import BaseFactory
from smartutils.error.base import BaseError
from smartutils.error.sys_err import SysError

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


class ExcFactory(BaseFactory[Type[BaseException], Callable[[BaseException], BaseError]]):
    @classmethod
    def get(cls, key: BaseException) -> BaseError:
        if isinstance(key, BaseError):
            return key

        for ext_type, handler in cls._registry.items():
            if isinstance(key, ext_type):
                return handler(key)

        return SysError(detail=str(key))


class JsonRespFactory(BaseFactory[AppKey, Callable[[BaseError], Any]]):
    pass


class ExcJsonResp:
    @classmethod
    def handle(cls, exc: BaseException, key: AppKey) -> Any:
        mapped_exc = ExcFactory.get(exc)
        resp_fn = JsonRespFactory.get(key)
        return resp_fn(mapped_exc)
