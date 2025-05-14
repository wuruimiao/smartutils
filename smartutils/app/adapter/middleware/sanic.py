from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin, AbstractMiddleware
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.sanic import SanicRequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.sanic import SanicResponseAdapter
from smartutils.app.const import AppKey
from smartutils.app.adapter.middleware.factory import MiddlewareFactory

__all__ = []


@MiddlewareFactory.register(AppKey.SANIC)
class SanicMiddleware(AbstractMiddleware):
    def __init__(self, plugin: AbstractMiddlewarePlugin):
        self._plugin = plugin

    def __call__(self, app):
        # Sanic 的中间件是 async def(request) or async def(request, response)
        @app.middleware("request")
        async def before_request(request):
            # 保存适配器到 request.ctx
            request.ctx._req_adapter = SanicRequestAdapter(request)

        @app.middleware("response")
        async def after_response(request, response):
            req: RequestAdapter = getattr(request.ctx, "_req_adapter", None)
            if req is None:
                req = SanicRequestAdapter(request)
            resp = SanicResponseAdapter(response)

            async def next_adapter():
                return resp

            # 调用插件
            result: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
            return result.response

        return app
