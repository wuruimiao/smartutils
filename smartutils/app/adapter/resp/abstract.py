from abc import ABC, abstractmethod
from smartutils.app.const import HeaderKey


class ResponseAdapter(ABC):
    def __init__(self, response):
        self.response = response

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
