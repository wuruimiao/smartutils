from abc import ABC, abstractmethod
from typing import Any, AsyncContextManager, List, Optional, Union


class AbstractSafeQueue(ABC):
    """安全任务队列抽象基类，定义通用接口。"""

    @abstractmethod
    async def task_num(self, queue: str) -> int: ...
    @abstractmethod
    async def enqueue_task(self, queue: str, task: Any) -> bool: ...
    @abstractmethod
    async def is_task_pending(self, pending: str, task: Any) -> bool: ...
    @abstractmethod
    def fetch_task_ctx(
        self, queue: str, pending: str, priority: Optional[Union[int, float]] = None
    ) -> AsyncContextManager[Optional[str]]: ...
    @abstractmethod
    async def requeue_task(
        self,
        queue: str,
        pending: str,
        task: Any,
        priority: Optional[Union[int, float]] = None,
    ) -> bool: ...
    @abstractmethod
    async def get_pending_members(
        self,
        pending: str,
        min_score: Optional[Union[int, float]] = None,
        max_score: Optional[Union[int, float]] = None,
        limit: int = 1,
    ) -> List[Any]: ...
