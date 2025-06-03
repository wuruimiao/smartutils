import base64
from typing import List, Optional

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.const import HeaderKey
from smartutils.log import logger

__all__ = ["CustomHeader"]


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
        return base64.b64decode(username).decode('utf-8')

    @classmethod
    def traceid(cls, adapter: RequestAdapter):
        return adapter.get_header(HeaderKey.X_TRACE_ID)

    @classmethod
    def permission_user_ids(cls, adapter: RequestAdapter) -> Optional[List[int]]:
        ids = adapter.get_header(HeaderKey.X_P_USER_IDS)
        if not ids:
            return None
        if not isinstance(ids, str):
            logger.error("CustomHeader get {ids}, not str, {type}", ids=ids, type=type(ids))
            return None
        return [int(s) for s in ids.split(",")]
