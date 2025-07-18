from abc import ABC, abstractmethod
from typing import Awaitable, Callable

from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import AppKey
from smartutils.config.schema.middleware import MiddlewarePluginSetting
from smartutils.error.sys import LibraryError

__all__ = ["AbstractMiddlewarePlugin", "AbstractMiddleware"]


class AbstractMiddlewarePlugin(ABC):
    def __init__(self, app_key: AppKey, conf: MiddlewarePluginSetting):
        self.app_key: AppKey = app_key
        self._resp_fn = JsonRespFactory.get(app_key)
        self._conf: MiddlewarePluginSetting = conf

    @abstractmethod
    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        pass


class AbstractMiddleware(ABC):

    def __init__(self, plugin: AbstractMiddlewarePlugin):
        self._plugin = plugin
        key = getattr(self.__class__, "_key", None)
        if not key:
            raise LibraryError(f"{self.__class__.__name__} need _key attr")
        self._req_adapter = RequestAdapterFactory.get(key)
        self._resp_adapter = ResponseAdapterFactory.get(key)

    def req_adapter(self, request):
        return self._req_adapter(request)

    def resp_adapter(self, response):
        return self._resp_adapter(response)
