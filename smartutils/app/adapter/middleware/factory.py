from typing import Callable

from smartutils.app.adapter.middleware.abstract import AbstractMiddleware, AbstractMiddlewarePlugin
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory

__all__ = ["MiddlewareFactory", "AddMiddlewareFactory"]


class MiddlewareFactory(BaseFactory[AppKey, AbstractMiddleware]):
    pass


class AddMiddlewareFactory(BaseFactory[AppKey, Callable[[object, AbstractMiddlewarePlugin], None]]):
    pass
