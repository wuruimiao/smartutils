from smartutils.app.adapter.middleware.abstract import AbstractMiddleware
from smartutils.app.adapter.middleware.factory import MiddlewareFactory
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey

__all__ = []

key = AppKey.DJANGO


@MiddlewareFactory.register(key)
class DjangoMiddleware(AbstractMiddleware):
    _key = key

    def __call__(self, get_response):
        # 检查是否异步视图
        import asyncio

        is_async = asyncio.iscoroutinefunction(get_response)

        if is_async:

            async def async_middleware(request):
                req: RequestAdapter = self.req_adapter(request)

                async def next_adapter():
                    response = await get_response(request)
                    return self.resp_adapter(response)

                resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
                return resp.response

            return async_middleware
        else:

            def sync_middleware(request):
                req: RequestAdapter = self.req_adapter(request)

                async def next_adapter():
                    response = get_response(request)
                    return self.resp_adapter(response)

                import asyncio

                resp: ResponseAdapter = asyncio.run(
                    self._plugin.dispatch(req, next_adapter)
                )
                return resp.response

            return sync_middleware
