from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, AsyncContextManager, List, Optional, TypeVar, Union

from smartutils.infra.cache.common.decode import DecodeBytes
from smartutils.infra.cache.ext.zset import ZSetHelper

try:
    from redis.asyncio import Redis
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import Redis

TaskID = Union[str, int]
TaskPriority = Union[int, float]


@dataclass
class Task:
    id: TaskID
    priority: TaskPriority = 0

    @property
    def ID(self) -> str:
        if isinstance(self.id, str):
            return self.id
        return str(self.id)


class AbstractSafeQueue(ABC):
    """安全任务队列抽象基类，定义通用接口。"""

    def __init__(self, redis_cli: Redis, decode_bytes: DecodeBytes):
        self._redis: Redis = redis_cli
        self._decode_bytes = decode_bytes

    @abstractmethod
    async def task_num(self, queue: str) -> int: ...
    @abstractmethod
    async def enqueue_task(self, queue: str, tasks: List[Task]) -> bool: ...
    @abstractmethod
    async def is_task_pending(self, pending: str, task: TaskID) -> bool: ...
    @abstractmethod
    def fetch_task_ctx(
        self, queue: str, pending: str
    ) -> AsyncContextManager[Optional[TaskID]]: ...
    @abstractmethod
    async def requeue_task(
        self,
        queue: str,
        pending: str,
        task: TaskID,
        priority: Optional[TaskPriority] = None,
    ) -> bool: ...

    async def get_pending_members(
        self,
        pending: str,
        min_priority: Optional[TaskPriority] = None,
        max_priority: Optional[TaskPriority] = None,
        limit: int = 1,
    ) -> List[TaskID]:
        members = await ZSetHelper.peek(
            self._redis, pending, min_priority, max_priority, limit
        )
        members = [self._decode_bytes.post(m) for m in members]
        # 取出按时间戳从大到小，实际需要从早到晚
        members.reverse()
        return members  # type: ignore


AbstractSafeQueueT = TypeVar("AbstractSafeQueueT", bound=AbstractSafeQueue)
