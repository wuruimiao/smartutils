import asyncio

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin, AbstractMiddleware
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.flask import FlaskRequestAdapter
from smartutils.app.adapter.resp.flask import FlaskResponseAdapter
from smartutils.app.const import AppKey
from smartutils.app.adapter.middleware.factory import MiddlewareFactory

__all__ = []


@MiddlewareFactory.register(AppKey.FLASK)
class FlaskMiddleware(AbstractMiddleware):
    def __init__(self, plugin: AbstractMiddlewarePlugin):
        self._plugin = plugin

    def __call__(self, app):
        # 装饰 Flask 应用，注册 before_request 和 after_request 钩子
        @app.before_request
        def before_request():
            # 在 Flask 里，before_request 不能获取响应对象
            # 但可以保存开始时间，或其他 request 相关信息
            import flask
            flask.g._middleware_req_adapter = FlaskRequestAdapter(flask.request)
            flask.g._middleware_start = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else None

        @app.after_request
        def after_request(response):
            import flask
            req: RequestAdapter = getattr(flask.g, "_middleware_req_adapter", None)
            if req is None:
                req = FlaskRequestAdapter(flask.request)
            resp = FlaskResponseAdapter(response)

            async def next_adapter():
                return resp

            # 兼容异步/同步
            if asyncio.iscoroutinefunction(self._plugin.dispatch):
                result = asyncio.run(self._plugin.dispatch(req, next_adapter))
            else:
                result = self._plugin.dispatch(req, next_adapter)
            # result 应该是 ResponseAdapter
            return result.response

        return app
