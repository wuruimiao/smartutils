from typing import Type

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory

__all__ = ["RequestAdapterFactory"]


class RequestAdapterFactory(BaseFactory[AppKey, Type[RequestAdapter], None]):
    """
    管理：不同应用框架下，如何构造对应的请求参数适配器，以在中间件中统一访问请求对象。
    """

    ...
