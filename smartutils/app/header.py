import base64

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.const import HeaderKey

__all__ = ["CustomHeader"]


class CustomHeader:
    @classmethod
    def userid(cls, adapter: RequestAdapter):
        return adapter.get_header(HeaderKey.X_USER_ID)

    @classmethod
    def username(cls, adapter: RequestAdapter):
        return base64.b64decode(adapter.get_header(HeaderKey.X_USER_NAME)).decode('utf-8')

    @classmethod
    def traceid(cls, adapter: RequestAdapter):
        return adapter.get_header(HeaderKey.X_TRACE_ID)
