from typing import Callable, Awaitable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import HEADERKeys
from smartutils.app.header import CustomHeader
from smartutils.ctx import CTXKeys, CTXVarManager


@CTXVarManager.register(CTXKeys.USERID)
@CTXVarManager.register(CTXKeys.USERNAME)
@CTXVarManager.register(CTXKeys.TRACE_ID)
class HeaderPlugin(AbstractMiddlewarePlugin):
    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        trace_id = CustomHeader.traceid(req)
        if not trace_id:
            trace_id = req.gen_trace_id()
        userid = CustomHeader.userid(req)
        username = CustomHeader.username(req)
        with (
            CTXVarManager.use(CTXKeys.TRACE_ID, trace_id),
            CTXVarManager.use(CTXKeys.USERID, userid),
            CTXVarManager.use(CTXKeys.USERNAME, username),
        ):
            resp: ResponseAdapter = await next_adapter()
            resp.set_header(HEADERKeys.X_TRACE_ID, trace_id)
            return resp
