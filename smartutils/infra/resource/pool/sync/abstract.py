from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import AsyncContextManager


class PoolSync(ABC):
    @abstractmethod
    def lock(self) -> AbstractContextManager: ...

    @abstractmethod
    def wait(self, timeout=None): ...

    @abstractmethod
    def notify(self): ...

    @abstractmethod
    def start_background_task(self, fn): ...


class PoolSyncAsync(ABC):
    @abstractmethod
    def lock(self) -> AsyncContextManager: ...

    @abstractmethod
    async def wait(self, timeout=None): ...

    @abstractmethod
    async def notify(self): ...

    @abstractmethod
    def start_background_task(self, fn): ...
