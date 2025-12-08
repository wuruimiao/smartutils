from typing import Type

from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory

__all__ = ["ResponseAdapterFactory"]

"""
管理：不同应用框架下，如何构造对应的响应适配器，以在中间件中统一访问响应对象。
"""


class ResponseAdapterFactory(BaseFactory[AppKey, Type[ResponseAdapter], None]): ...
