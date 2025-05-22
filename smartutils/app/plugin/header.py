from typing import Callable, Awaitable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import HeaderKey, MiddlewarePluginKey, MiddlewarePluginOrder
from smartutils.app.header import CustomHeader
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.ctx import CTXKey, CTXVarManager

__all__ = ["HeaderPlugin"]


@MiddlewarePluginFactory.register(MiddlewarePluginKey.HEADER, order=MiddlewarePluginOrder.HEADER)
class HeaderPlugin(AbstractMiddlewarePlugin):
    async def dispatch(
            self,
            req: RequestAdapter,
            next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        trace_id = CustomHeader.traceid(req)
        if not trace_id:
            trace_id = req.gen_trace_id()
        userid = CustomHeader.userid(req) or "0"
        username = CustomHeader.username(req) or "''"
        with (
            CTXVarManager.use(CTXKey.TRACE_ID, trace_id),
            CTXVarManager.use(CTXKey.USERID, userid),
            CTXVarManager.use(CTXKey.USERNAME, username),
        ):
            resp: ResponseAdapter = await next_adapter()
            resp.set_header(HeaderKey.X_TRACE_ID, trace_id)
            return resp
