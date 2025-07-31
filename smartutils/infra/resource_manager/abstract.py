from abc import ABC, abstractmethod
from typing import Any, AsyncContextManager, TypeVar

__all__ = ["AbstractResource", "T"]


class AbstractResource(ABC):
    @abstractmethod
    async def close(self):
        """关闭资源"""
        pass

    @abstractmethod
    async def ping(self) -> bool:
        """健康检查，返回True/False"""
        pass

    @abstractmethod
    def db(self, use_transaction: bool) -> AsyncContextManager[Any]:
        pass


T = TypeVar("T", bound=AbstractResource)
