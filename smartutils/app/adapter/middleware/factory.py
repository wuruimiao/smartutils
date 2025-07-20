from typing import Any, Callable, List

from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddlewarePlugin,
)
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory

__all__ = ["AddMiddlewareFactory"]


class AddMiddlewareFactory(
    BaseFactory[AppKey, Callable[[object, List[AbstractMiddlewarePlugin]], None]]
):
    pass


class RouteMiddlewareFactory(
    BaseFactory[AppKey, Callable[[List[AbstractMiddlewarePlugin]], Any]]
):
    pass
