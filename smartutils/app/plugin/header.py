import base64
from typing import Callable, Awaitable, List, Optional

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import HeaderKey
from smartutils.app.const import MiddlewarePluginKey, MiddlewarePluginOrder
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.log import logger

__all__ = ["HeaderPlugin"]


class CustomHeader:
    @classmethod
    def userid(cls, adapter: RequestAdapter) -> int:
        userid = adapter.get_header(HeaderKey.X_USER_ID)
        if not userid:
            return 0
        return int(userid)

    @classmethod
    def username(cls, adapter: RequestAdapter) -> str:
        username = adapter.get_header(HeaderKey.X_USER_NAME)
        if not username:
            return ""
        return base64.b64decode(username).decode("utf-8")

    @classmethod
    def traceid(cls, adapter: RequestAdapter):
        return adapter.get_header(HeaderKey.X_TRACE_ID)

    @classmethod
    def permission_user_ids(cls, adapter: RequestAdapter) -> Optional[List[int]]:
        ids = adapter.get_header(HeaderKey.X_P_USER_IDS)
        if not ids:
            return None
        if not isinstance(ids, str):
            logger.error(
                "CustomHeader get {ids}, not str, {type}", ids=ids, type=type(ids)
            )
            return None
        return [int(s) for s in ids.split(",")]


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.HEADER, order=MiddlewarePluginOrder.HEADER
)
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
        permission_user_ids = CustomHeader.permission_user_ids(req)
        with (
            CTXVarManager.use(CTXKey.TRACE_ID, trace_id),
            CTXVarManager.use(CTXKey.USERID, userid),
            CTXVarManager.use(CTXKey.USERNAME, username),
            CTXVarManager.use(CTXKey.PERMISSION_USER_IDS, permission_user_ids),
        ):
            resp: ResponseAdapter = await next_adapter()
            resp.set_header(HeaderKey.X_TRACE_ID, trace_id)
            return resp
