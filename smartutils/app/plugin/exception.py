from typing import Callable, Awaitable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import MiddlewarePluginKey, MiddlewarePluginOrder
from smartutils.app.plugin.factory import MiddlewarePluginFactory

__all__ = ["ExceptionPlugin"]


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.EXCEPTION, order=MiddlewarePluginOrder.EXCEPTION
)
class ExceptionPlugin(AbstractMiddlewarePlugin):
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

            return ExcJsonResp(self.app_key).handle(exc)
