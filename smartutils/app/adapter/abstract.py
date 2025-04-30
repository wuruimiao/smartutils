from abc import ABC, abstractmethod


class RequestAdapter(ABC):
    def __init__(self, request):
        self.request = request

    @property
    @abstractmethod
    def headers(self):
        pass

    @property
    @abstractmethod
    def query_params(self):
        pass

    @property
    @abstractmethod
    def client_host(self):
        pass

    @property
    @abstractmethod
    def method(self):
        pass

    @property
    @abstractmethod
    def url(self):
        pass
