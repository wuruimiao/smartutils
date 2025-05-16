import asyncio

import flask
from smartutils.app.adapter.middleware.abstract import AbstractMiddleware
from smartutils.app.adapter.middleware.factory import MiddlewareFactory
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.const import AppKey

__all__ = []

key = AppKey.FLASK


@MiddlewareFactory.register(key)
class FlaskMiddleware(AbstractMiddleware):
    _key = key

    def __call__(self, app):
        # 装饰 Flask 应用，注册 before_request 和 after_request 钩子
        @app.before_request
        def before_request():
            # 在 Flask 里，before_request 不能获取响应对象
            # 但可以保存开始时间，或其他 request 相关信息
            flask.g._middleware_req_adapter = self.req_adapter(flask.request)
            flask.g._middleware_start = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else None

        @app.after_request
        def after_request(response):
            req: RequestAdapter = getattr(flask.g, "_middleware_req_adapter", None)
            if req is None:
                req = self.req_adapter(flask.request)
            resp = self.resp_adapter(response)

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
