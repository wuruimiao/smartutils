from typing import Awaitable, Callable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import MiddlewarePluginOrder
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import MiddlewarePluginKey

__all__ = ["ExceptionPlugin"]

key = MiddlewarePluginKey.EXCEPTION


@MiddlewarePluginFactory.register(key, order=MiddlewarePluginOrder.EXCEPTION)
class ExceptionPlugin(AbstractMiddlewarePlugin):
    _key = key

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
