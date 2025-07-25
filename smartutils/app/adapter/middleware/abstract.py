from abc import ABC, abstractmethod
from typing import Awaitable, Callable, List, TypeVar

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

__all__ = ["AbstractMiddlewarePlugin", "AbstractMiddleware", "chain_dispatch"]


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


RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")


def chain_dispatch(
    plugins: List[AbstractMiddlewarePlugin],
    handler: Callable[[RequestT], Awaitable[ResponseT]],
) -> Callable[[RequestT], Awaitable[ResponseT]]:

    req_adapter = RequestAdapterFactory.get(RunEnv.get_app())
    resp_adapter = ResponseAdapterFactory.get(RunEnv.get_app())

    async def dispatch_from(i: int, request: RequestT) -> ResponseT:
        if i >= len(plugins):
            return await handler(request)
        plugin = plugins[i]
        req = req_adapter(request)

        async def next_call() -> ResponseAdapter:
            response = await dispatch_from(i + 1, request)
            return resp_adapter(response)

        resp: ResponseAdapter = await plugin.dispatch(req, next_call)
        return resp.response

    async def entry(request: RequestT) -> ResponseT:
        return await dispatch_from(0, request)

    return entry
