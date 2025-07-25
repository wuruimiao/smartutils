from abc import ABC, abstractmethod
from typing import Awaitable, Callable

from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import AppKey, RunEnv
from smartutils.app.factory import ExcJsonResp
from smartutils.config.schema.middleware import (
    MiddlewarePluginKey,
    MiddlewarePluginSetting,
)

__all__ = ["AbstractMiddlewarePlugin", "AbstractMiddleware"]


class AbstractMiddlewarePlugin(ABC):
    def __init__(self, *, conf: MiddlewarePluginSetting):
        self.key: MiddlewarePluginKey
        self._app_key: AppKey = RunEnv.get_app()
        self._resp_fn = JsonRespFactory.get(self._app_key)
        self._exc_resp = ExcJsonResp()
        self._conf: MiddlewarePluginSetting = conf

    @abstractmethod
    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        pass


class AbstractMiddleware(ABC):
    def __init__(self, *, plugin: AbstractMiddlewarePlugin, app_key: AppKey, **kwargs):
        self._plugin = plugin
        self._req_adapter = RequestAdapterFactory.get(app_key)
        self._resp_adapter = ResponseAdapterFactory.get(app_key)
        super().__init__(**kwargs)

    def req_adapter(self, request):
        return self._req_adapter(request)

    def resp_adapter(self, response):
        return self._resp_adapter(response)
