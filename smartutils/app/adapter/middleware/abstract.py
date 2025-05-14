from abc import ABC, abstractmethod
from typing import Callable, Awaitable

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter

__all__ = ["AbstractMiddlewarePlugin", "AbstractMiddleware"]


class AbstractMiddlewarePlugin(ABC):
    @abstractmethod
    async def dispatch(
            self,
            req: RequestAdapter,
            next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        pass


class AbstractMiddleware(ABC):
    pass
