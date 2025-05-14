from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin, AbstractMiddleware
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import AppKey
from smartutils.app.adapter.middleware.factory import MiddlewareFactory

__all__ = []

key = AppKey.DJANGO


@MiddlewareFactory.register(key)
class DjangoMiddleware(AbstractMiddleware):
    def __init__(self, plugin: AbstractMiddlewarePlugin):
        self._plugin = plugin

    def __call__(self, get_response):
        # 检查是否异步视图
        import asyncio
        is_async = asyncio.iscoroutinefunction(get_response)

        if is_async:
            async def middleware(request):
                req: RequestAdapter = RequestAdapterFactory.get(key)(request)

                async def next_adapter():
                    response = await get_response(request)
                    return ResponseAdapterFactory.get(key)(response)

                resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
                return resp.response

            return middleware
        else:
            def middleware(request):
                req: RequestAdapter = RequestAdapterFactory.get(key)(request)

                async def next_adapter():
                    response = get_response(request)
                    return ResponseAdapterFactory.get(key)(response)

                import asyncio
                resp: ResponseAdapter = asyncio.run(self._plugin.dispatch(req, next_adapter))
                return resp.response

            return middleware
