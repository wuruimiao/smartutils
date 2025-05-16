from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory

__all__ = ["RequestAdapterFactory"]


class RequestAdapterFactory(BaseFactory[AppKey, RequestAdapter]):
    pass
