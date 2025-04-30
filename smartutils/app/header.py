from smartutils.app.adapter import RequestAdapter
from smartutils.app.const import HEADERKeys


class CustomHeader:
    @classmethod
    def userid(cls, adapter: RequestAdapter):
        return adapter.headers.get(HEADERKeys.X_USER_ID)

    @classmethod
    def username(cls, adapter: RequestAdapter):
        return adapter.headers.get(HEADERKeys.X_USER_NAME)

    @classmethod
    def traceid(cls, adapter: RequestAdapter):
        return adapter.headers.get(HEADERKeys.X_TRACE_ID)
