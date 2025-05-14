from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin, AbstractMiddleware
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import AppKey
from smartutils.app.adapter.middleware.factory import MiddlewareFactory

__all__ = []

key = AppKey.TORNADO


@MiddlewareFactory.register(key)
class TornadoMiddleware(AbstractMiddleware):
    def __init__(self, plugin: AbstractMiddlewarePlugin):
        self._plugin = plugin

    def __call__(self, app):
        # patch 原始 Application.__call__
        original_call = app.__call__

        async def patched_call(request):
            req: RequestAdapter = RequestAdapterFactory.get(key)(request)

            async def next_adapter():
                response = await original_call(request)
                return ResponseAdapterFactory.get(key)(response)

            resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
            return resp.response

        app.__call__ = patched_call
        return app
