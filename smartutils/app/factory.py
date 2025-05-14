from typing import List, Awaitable, Callable, Any

from loguru import logger

from smartutils.app.const import AppKey
from smartutils.design import BaseFactory
from smartutils.error.base import BaseError
from smartutils.error.factory import ExcFactory, ExcFormatFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter

__all__ = ["AppHook", "JsonRespFactory", "ExcJsonResp"]


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


class JsonRespFactory(BaseFactory[AppKey, Callable[[BaseError], ResponseAdapter]]):
    pass


class ExcJsonResp:
    @classmethod
    def handle(cls, exc: BaseException, key: AppKey) -> ResponseAdapter:
        mapped_exc = ExcFactory.get(exc)
        resp_fn = JsonRespFactory.get(key)
        logger.error("ExcJsonResp handle {e}", e=ExcFormatFactory.get(exc))
        return resp_fn(mapped_exc)
