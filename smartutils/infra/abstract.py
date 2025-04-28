from abc import ABC, abstractmethod
from typing import Dict, Callable, Any, Awaitable, TypeVar, Generic, AsyncContextManager


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


T = TypeVar("T", bound=AbstractResource)
