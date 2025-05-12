from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.starlette import StarletteRequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.starlette import StarletteResponseAdapter

__all__ = ["StarletteMiddleware"]


class StarletteMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, plugin: AbstractMiddlewarePlugin):
        super().__init__(app)
        self._plugin = plugin

    async def dispatch(self, request: Request, call_next):
        req: RequestAdapter = StarletteRequestAdapter(request)

        async def next_adapter():
            response: Response = await call_next(request)
            return StarletteResponseAdapter(response)

        resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
        return resp.response
