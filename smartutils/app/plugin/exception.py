from typing import Callable, Awaitable
from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter

__all__ = ["ExceptionPlugin"]


class ExceptionPlugin(AbstractMiddlewarePlugin):
    def __init__(self, app_key):
        self.app_key = app_key

    async def dispatch(
            self,
            req: RequestAdapter,
            next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        try:
            resp = await next_adapter()
            return resp
        except Exception as exc:
            from smartutils.app.factory import ExcJsonResp
            from smartutils.app.const import AppKey

            return ExcJsonResp.handle(exc, self.app_key)
