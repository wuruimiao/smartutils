from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.const import HEADERKeys


class CustomHeader:
    @classmethod
    def userid(cls, adapter: RequestAdapter):
        return adapter.get_header(HEADERKeys.X_USER_ID)

    @classmethod
    def username(cls, adapter: RequestAdapter):
        return adapter.get_header(HEADERKeys.X_USER_NAME)

    @classmethod
    def traceid(cls, adapter: RequestAdapter):
        return adapter.get_header(HEADERKeys.X_TRACE_ID)
