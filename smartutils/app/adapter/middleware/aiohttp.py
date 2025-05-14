from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin, AbstractMiddleware
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.aiohttp import AIOHTTPRequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.aiohttp import AiohttpResponseAdapter
from smartutils.app.adapter.middleware.factory import MiddlewareFactory
from smartutils.app.const import AppKey

__all__ = []


@MiddlewareFactory.register(AppKey.AIOHTTP)
class AiohttpMiddleware(AbstractMiddleware):
    def __init__(self, plugin: AbstractMiddlewarePlugin):
        self._plugin = plugin

    def __call__(self, app):
        async def middleware(request, handler):
            req: RequestAdapter = AIOHTTPRequestAdapter(request)

            async def next_adapter():
                response = await handler(request)
                return AiohttpResponseAdapter(response)

            resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
            return resp.response

        return middleware
