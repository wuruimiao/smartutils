from smartutils.app.adapter.middleware.abstract import AbstractMiddleware
from smartutils.app.adapter.middleware.factory import MiddlewareFactory
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey

__all__ = []

key = AppKey.TORNADO


@MiddlewareFactory.register(AppKey.TORNADO)
class TornadoMiddleware(AbstractMiddleware):
    _key = key

    def __call__(self, app):
        # patch 原始 Application.__call__
        original_call = app.__call__

        async def patched_call(request):
            req: RequestAdapter = self.req_adapter(request)

            async def next_adapter():
                response = await original_call(request)
                return self.resp_adapter(response)

            resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
            return resp.response

        app.__call__ = patched_call
        return app
