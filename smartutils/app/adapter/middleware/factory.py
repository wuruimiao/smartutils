from typing import Any, Callable, Tuple

from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddlewarePlugin,
)
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory

__all__ = ["AddMiddlewareFactory"]


class AddMiddlewareFactory(
    BaseFactory[AppKey, Callable[[object, Tuple[AbstractMiddlewarePlugin]], None]]
):
    pass


class RouteMiddlewareFactory(
    BaseFactory[AppKey, Callable[[Tuple[AbstractMiddlewarePlugin]], Any]]
):
    pass


class EndpointMiddlewareFactory(
    BaseFactory[AppKey, Callable[[Tuple[AbstractMiddlewarePlugin]], Any]]
):
    pass
