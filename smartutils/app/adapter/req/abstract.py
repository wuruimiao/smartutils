from abc import ABC, abstractmethod
from typing import Generic, Mapping, TypeVar

from smartutils.app.const import HeaderKey
from smartutils.ID import IDGen

__all__ = ["RequestAdapter"]

T = TypeVar("T")


class RequestAdapter(ABC, Generic[T]):
    """
    定义请求参数适配器的抽象基类，封装对请求对象的统一访问接口。
    不同 Web 框架可实现此接口以适配各自的请求对象。
    主要功能包括获取请求头、查询参数、客户端信息、HTTP 方法、URL、路径和 Cookie 等。
    还提供生成唯一请求追踪 ID 的方法，便于日志记录和调试。
    """

    def __init__(self, request: T):
        self._request: T = request

    @property
    def request(self) -> T:
        return self._request

    @abstractmethod
    def get_header(self, key: HeaderKey) -> str: ...

    @abstractmethod
    def set_header(self, key: HeaderKey, value: str): ...

    @property
    @abstractmethod
    def headers(self) -> Mapping[str, str]: ...

    @property
    @abstractmethod
    def query_params(self) -> dict: ...

    @property
    @abstractmethod
    def client_host(self) -> str: ...

    @property
    @abstractmethod
    def method(self) -> str: ...

    @property
    @abstractmethod
    def url(self) -> str: ...

    @property
    @abstractmethod
    def path(self) -> str: ...

    @abstractmethod
    def get_cookie(self, key: str) -> str: ...

    def gen_trace_id(self) -> str:
        return str(IDGen())
