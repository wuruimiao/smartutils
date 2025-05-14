from abc import ABC, abstractmethod
from typing import TypeVar, AsyncContextManager

__all__ = ["AbstractResource", "TAbstractResource"]


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
    async def session(self) -> AsyncContextManager:
        pass


TAbstractResource = TypeVar("TAbstractResource", bound=AbstractResource)
