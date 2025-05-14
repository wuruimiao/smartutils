from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin, AbstractMiddleware
from smartutils.app.adapter.middleware.factory import MiddlewareFactory
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey

__all__ = []

key = AppKey.FASTAPI


@MiddlewareFactory.register(key)
class StarletteMiddleware(AbstractMiddleware, BaseHTTPMiddleware):
    def __init__(self, app, plugin: AbstractMiddlewarePlugin, req_adapter: type[RequestAdapter],
                 resp_adapter: type[ResponseAdapter]):
        BaseHTTPMiddleware.__init__(self, app)
        AbstractMiddleware.__init__(self, plugin, req_adapter, resp_adapter)
        self._plugin = plugin

    async def dispatch(self, request: Request, call_next):
        req: RequestAdapter = self.req_adapter(request)

        async def next_adapter():
            response: Response = await call_next(request)
            return self.resp_adapter(response)

        resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
        return resp.response
