from abc import ABC, abstractmethod
from typing import Any, AsyncContextManager, Optional, Sequence


class SafeQueue(ABC):
    """安全任务队列抽象基类，定义通用接口。"""

    @abstractmethod
    async def enqueue_task(self, queue: str, task: Any) -> bool: ...
    @abstractmethod
    async def is_task_pending(self, pending: str, task: Any) -> bool: ...
    @abstractmethod
    def fetch_task_ctx(
        self, queue: str, pending: str, priority: Any = None
    ) -> AsyncContextManager[Optional[str]]: ...
    @abstractmethod
    async def requeue_task(
        self, queue: str, pending: str, task: Any, priority: Any = None
    ) -> bool: ...
