from smartutils.app.const import AppKey
from smartutils.design import BaseFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter

__all__ = ["ResponseAdapterFactory"]


class ResponseAdapterFactory(BaseFactory[AppKey, ResponseAdapter]):
    pass
