from contextlib import asynccontextmanager

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import HEADERKeys
from smartutils.app.header import CustomHeader
from smartutils.ctx import CTXKeys, CTXVarManager


@CTXVarManager.register(CTXKeys.USERID)
@CTXVarManager.register(CTXKeys.USERNAME)
class HeaderPlugin(AbstractMiddlewarePlugin):
    @asynccontextmanager
    async def before_request(self, req: RequestAdapter):
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
            yield

    @asynccontextmanager
    async def after_request(self, req: RequestAdapter, resp: ResponseAdapter):
        trace_id = CTXVarManager.get(CTXKeys.TRACE_ID)
        resp.set_header(HEADERKeys.X_TRACE_ID, trace_id)
        yield
