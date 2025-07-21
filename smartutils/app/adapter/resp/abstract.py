from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from smartutils.app.const import HeaderKey

__all__ = ["ResponseAdapter"]

T = TypeVar("T")


class ResponseAdapter(ABC, Generic[T]):
    def __init__(self, response: T):
        self._response: T = response

    @abstractmethod
    def set_header(self, key: HeaderKey, value: str):
        """设置响应header"""
        pass

    @property
    @abstractmethod
    def status_code(self) -> int:
        """HTTP 状态码"""
        pass

    @status_code.setter
    @abstractmethod
    def status_code(self, value: int):
        pass

    @property
    def response(self):
        return self._response
