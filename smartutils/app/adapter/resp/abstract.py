from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from smartutils.app.const import HeaderKey

__all__ = ["ResponseAdapter"]

T = TypeVar("T")


class ResponseAdapter(ABC, Generic[T]):
    """
    定义响应适配器的抽象基类，封装对响应对象的统一访问接口。
    不同 Web 框架可实现此接口以适配各自的响应对象。
    主要功能包括设置响应头和状态码等。
    """

    def __init__(self, response: T):
        self._response: T = response

    @property
    def response(self) -> T:
        return self._response

    @abstractmethod
    def set_header(self, key: HeaderKey, value: str):
        """设置响应header"""
        ...

    @property
    @abstractmethod
    def status_code(self) -> int:
        """HTTP 状态码"""
        ...

    @status_code.setter
    @abstractmethod
    def status_code(self, value: int): ...
