from abc import ABC, abstractmethod
from smartutils.app.const import HeaderKey


class RequestAdapter(ABC):
    def __init__(self, request):
        self.request = request

    @abstractmethod
    def get_header(self, key: HeaderKey):
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
    def gen_trace_id(self) -> str:
        pass
