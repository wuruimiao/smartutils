from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from smartutils.app.fast.header import CustomHeader
from smartutils.app.const import HEADERKeys
from smartutils.ctx import CTXKeys, ContextVarManager


@ContextVarManager.register(CTXKeys.USERID)
@ContextVarManager.register(CTXKeys.USERNAME)
class HeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = CustomHeader.traceid(request)
        if not trace_id:
            trace_id = str(request.app.state.gen())

        userid = CustomHeader.userid(request)
        username = CustomHeader.username(request)

        with (
            ContextVarManager.use(CTXKeys.TRACE_ID, trace_id),
            ContextVarManager.use(CTXKeys.USERID, userid),
            ContextVarManager.use(CTXKeys.USERNAME, username),
        ):
            response = await call_next(request)

            response.headers[HEADERKeys.X_TRACE_ID] = trace_id
            return response
