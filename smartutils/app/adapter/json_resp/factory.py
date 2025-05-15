from typing import Callable

from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory
from smartutils.error.base import BaseError

__all__ = ["ErrorRespAdapterFactory"]


class ErrorRespAdapterFactory(BaseFactory[AppKey, Callable[[BaseError], ResponseAdapter]]):
    pass
