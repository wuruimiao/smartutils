from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin, AbstractMiddleware
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.tornado import TornadoRequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.tornado import TornadoResponseAdapter
from smartutils.app.const import AppKey
from smartutils.app.adapter.middleware.factory import MiddlewareFactory

__all__ = []


@MiddlewareFactory.register(AppKey.TORNADO)
class TornadoMiddleware(AbstractMiddleware):
    def __init__(self, plugin: AbstractMiddlewarePlugin):
        self._plugin = plugin

    def __call__(self, app):
        # patch 原始 Application.__call__
        original_call = app.__call__

        async def patched_call(request):
            req: RequestAdapter = TornadoRequestAdapter(request)

            async def next_adapter():
                response = await original_call(request)
                return TornadoResponseAdapter(response)

            resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
            return resp.response

        app.__call__ = patched_call
        return app
