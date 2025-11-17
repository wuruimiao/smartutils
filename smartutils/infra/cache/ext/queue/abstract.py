from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncContextManager, List, Optional, TypeVar, Union

TaskID = Union[str, int]
TaskPriority = Union[int, float]


@dataclass
class TaskInfo:
    id: TaskID
    priority: TaskPriority = 0

    @property
    def ID(self) -> str:
        if isinstance(self.id, str):
            return self.id
        return str(self.id)


class AbstractSafeQueue(ABC):
    """安全任务队列抽象基类，定义通用接口。"""

    @abstractmethod
    async def task_num(self, queue: str) -> int: ...
    @abstractmethod
    async def enqueue_task(self, queue: str, tasks: List[TaskInfo]) -> bool: ...
    @abstractmethod
    async def is_task_pending(self, pending: str, task: TaskID) -> bool: ...
    @abstractmethod
    def fetch_task_ctx(
        self, queue: str, pending: str, priority: Optional[TaskPriority] = None
    ) -> AsyncContextManager[Optional[TaskID]]: ...
    @abstractmethod
    async def requeue_task(
        self,
        queue: str,
        pending: str,
        task: TaskID,
        priority: Optional[TaskPriority] = None,
    ) -> bool: ...
    @abstractmethod
    async def get_pending_members(
        self,
        pending: str,
        min_priority: Optional[TaskPriority] = None,
        max_priority: Optional[TaskPriority] = None,
        limit: int = 1,
    ) -> List[Any]: ...


AbstractSafeQueueT = TypeVar("AbstractSafeQueueT", bound=AbstractSafeQueue)
