from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from smartutils.app.fast.header import CustomHeader
from smartutils.app.const import HEADERKeys
from smartutils.ctx import CTXKeys, CTXVarManager
from smartutils.log import logger
from smartutils.timer import Timer


class HeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = CustomHeader.traceid(request)
        if not trace_id:
            trace_id = str(request.app.state.gen())

        userid = CustomHeader.userid(request)
        username = CustomHeader.username(request)

        with (
            CTXVarManager.use(CTXKeys.TRACE_ID, trace_id),
            CTXVarManager.use(CTXKeys.USERID, userid),
            CTXVarManager.use(CTXKeys.USERNAME, username),
        ):
            response = await call_next(request)

            response.headers[HEADERKeys.X_TRACE_ID] = trace_id
            return response


class LoggMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        async with Timer() as t:
            response: Response = await call_next(request)
        client_host = request.client.host if request.client else "-"
        logger.info(
            f"{client_host} - '{request.method} {request.url}' - "
            f"Query: {dict(request.query_params)} "
            f"Status: {response.status_code} - "
            f"Cost: {t.elapsed:.3f} sec"
        )
        return response
