from typing import Any, Callable, Tuple

from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddlewarePlugin,
)
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory

__all__ = ["AddMiddlewareFactory"]


class AddMiddlewareFactory(
    BaseFactory[
        AppKey, Callable[[object, Tuple[AbstractMiddlewarePlugin, ...]], None], None
    ]
):
    """
    管理：具体应用框架，如何给应用添加中间件插件（可在应用初始化时使用）。
    """

    ...


class RouteMiddlewareFactory(
    BaseFactory[AppKey, Callable[[Tuple[AbstractMiddlewarePlugin, ...]], Any], None]
):
    """
    管理：具体应用框架，如何给路由添加中间件插件（可在应用初始化时使用）。
    """

    ...


class EndpointMiddlewareFactory(
    BaseFactory[AppKey, Callable[[Tuple[AbstractMiddlewarePlugin, ...]], Any], None]
):
    """
    管理：具体应用框架，如何给端点添加中间件插件（可在应用初始化时使用）。
    """

    ...
