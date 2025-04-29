from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from smartutils.app.fast.header import CustomHeader
from smartutils.ctx import CTXKey, ContextVarManager


class HeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = CustomHeader.traceid(request)
        if not trace_id:
            trace_id = str(request.app.state.gen())

        userid = CustomHeader.userid(request)
        username = CustomHeader.username(request)

        with (
            ContextVarManager.use(CTXKey.TRACE_ID, trace_id),
            ContextVarManager.use(CTXKey.USERID, userid),
            ContextVarManager.use(CTXKey.USERNAME, username),
        ):
            response = await call_next(request)

            response.headers[CTXKey.TRACE_ID] = trace_id
            return response
