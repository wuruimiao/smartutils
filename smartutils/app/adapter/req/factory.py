from smartutils.app.const import AppKey
from smartutils.design import BaseFactory
from smartutils.app.adapter.req.abstract import RequestAdapter

__all__ = ["RequestAdapterFactory"]


class RequestAdapterFactory(BaseFactory[AppKey, RequestAdapter]):
    pass
