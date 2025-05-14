from smartutils.app.const import AppKey
from smartutils.design import BaseFactory
from smartutils.app.adapter.middleware.abstract import AbstractMiddleware

__all__ = ["MiddlewareFactory"]


class MiddlewareFactory(BaseFactory[AppKey, AbstractMiddleware]):
    pass


# class AddMiddlewareFactory(BaseFactory[AppKey, ]):
#     pass
