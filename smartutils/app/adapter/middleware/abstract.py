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
    def __init__(self, plugin: AbstractMiddlewarePlugin, req_adapter: type[RequestAdapter],
                 resp_adapter: type[ResponseAdapter]):
        self._plugin = plugin
        self._req_adapter = req_adapter
        self._resp_adapter = resp_adapter

    def req_adapter(self, request):
        return self._req_adapter(request)

    def resp_adapter(self, response):
        return self._resp_adapter(response)
