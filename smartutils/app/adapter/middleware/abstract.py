from abc import ABC, abstractmethod
from typing import Callable, Awaitable

__all__ = ["AbstractMiddlewarePlugin"]

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter


class AbstractMiddlewarePlugin(ABC):
    @abstractmethod
    async def dispatch(
            self,
            req: RequestAdapter,
            next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        pass
