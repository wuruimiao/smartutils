from abc import ABC, abstractmethod

from smartutils.app.const import HeaderKey
from smartutils.ID import IDGen

__all__ = ["RequestAdapter"]


class RequestAdapter(ABC):
    def __init__(self, request):
        self.request = request

    @abstractmethod
    def get_header(self, key: HeaderKey) -> str:
        pass

    @abstractmethod
    def set_header(self, key: HeaderKey, value: str):
        pass

    @property
    @abstractmethod
    def headers(self) -> dict:
        pass

    @property
    @abstractmethod
    def query_params(self) -> dict:
        pass

    @property
    @abstractmethod
    def client_host(self) -> str:
        pass

    @property
    @abstractmethod
    def method(self) -> str:
        pass

    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @abstractmethod
    def get_cookie(self, key: str) -> str:
        pass

    def gen_trace_id(self) -> str:
        return str(IDGen())
