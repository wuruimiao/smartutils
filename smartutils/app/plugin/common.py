import base64
from typing import Dict, List, Optional

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.const import HeaderKey
from smartutils.log import logger


class CustomHeader:
    @classmethod
    def userid(cls, adapter: RequestAdapter, value: Optional[int] = None) -> int:
        if value is not None:
            adapter.set_header(HeaderKey.X_USER_ID, str(value))
            return 0

        userid = adapter.get_header(HeaderKey.X_USER_ID)
        if not userid:
            return 0
        return int(userid)

    @classmethod
    def username(cls, adapter: RequestAdapter, value: Optional[str] = None) -> str:
        if value is not None:
            adapter.set_header(
                HeaderKey.X_USER_NAME,
                base64.b64encode(value.encode("utf-8")).decode("utf-8"),
            )
            return ""

        username = adapter.get_header(HeaderKey.X_USER_NAME)
        if not username:
            return ""
        return base64.b64decode(username).decode("utf-8")

    @classmethod
    def traceid(cls, adapter: RequestAdapter):
        return adapter.get_header(HeaderKey.X_TRACE_ID)

    @classmethod
    def permission_user_ids(
        cls, adapter: RequestAdapter, value: Optional[List[int]] = None
    ) -> Optional[List[int]]:
        if value is not None:
            adapter.set_header(
                HeaderKey.X_P_USER_IDS, ",".join([str(i) for i in value])
            )
            return

        ids = adapter.get_header(HeaderKey.X_P_USER_IDS)
        if not ids:
            return None
        if not isinstance(ids, str):
            logger.error(
                "CustomHeader get {ids}, not str, {type}", ids=ids, type=type(ids)
            )
            return None
        return [int(s) for s in ids.split(",")]


def get_auth_cookies(req: RequestAdapter) -> Dict:
    # TODO: access_token配置化
    access_token = "access_token"
    value = req.get_cookie(access_token)
    if not value:
        logger.error(f"get_auth_cookies request no {access_token}")
        return {}
    return {access_token: value}
