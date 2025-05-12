from enum import Enum


class HeaderKey(str, Enum):
    X_USER_ID = "X-User-Id"
    X_USER_NAME = "X-User-Name"
    X_TRACE_ID = "X-Trace-ID"


class AppKey(Enum):
    FASTAPI = "fastapi"

    @classmethod
    def list(cls):
        return [e.value for e in cls]
