from smartutils.app.adapter.middleware.abstract import AbstractMiddleware
from smartutils.app.adapter.middleware.factory import MiddlewareFactory
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey

__all__ = []

key = AppKey.AIOHTTP


@MiddlewareFactory.register(key)
class AiohttpMiddleware(AbstractMiddleware):
    _key = key

    def __call__(self, app):
        async def middleware(request, handler):
            req: RequestAdapter = self.req_adapter(request)

            async def next_adapter():
                response = await handler(request)
                return self.resp_adapter(response)

            resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
            return resp.response

        return middleware
