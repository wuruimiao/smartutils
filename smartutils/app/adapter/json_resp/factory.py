from typing import Callable

from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory
from smartutils.error.base import BaseDataDict

__all__ = ["JsonRespFactory"]


class JsonRespFactory(
    BaseFactory[AppKey, Callable[[BaseDataDict], ResponseAdapter], None]
):
    """
    管理：具体应用框架，拿到异常/正常响应数据后，如何构造对应的通用 JSON 响应适配器（可在中间件/其他地方使用）。
    """

    ...
