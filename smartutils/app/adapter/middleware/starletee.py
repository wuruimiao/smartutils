from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin, AbstractMiddleware
from smartutils.app.adapter.middleware.factory import MiddlewareFactory
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import AppKey

__all__ = []

key = AppKey.FASTAPI


@MiddlewareFactory.register(key)
class StarletteMiddleware(AbstractMiddleware, BaseHTTPMiddleware):
    def __init__(self, app, plugin: AbstractMiddlewarePlugin):
        super().__init__(app)
        self._plugin = plugin

    async def dispatch(self, request: Request, call_next):
        req: RequestAdapter = RequestAdapterFactory.get(key)(request)

        async def next_adapter():
            response: Response = await call_next(request)
            return ResponseAdapterFactory.get(key)(response)

        resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
        return resp.response
