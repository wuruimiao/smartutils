from enum import Enum

__all__ = ["HeaderKey", "AppKey"]


class HeaderKey(str, Enum):
    X_USER_ID = "X-User-Id"
    X_USER_NAME = "X-User-Name"
    X_TRACE_ID = "X-Trace-ID"


class AppKey(Enum):
    AIOHTTP = "aiohttp"
    DJANGO = "django"
    FLASK = "flask"
    SANIC = "sanic"
    FASTAPI = "fastapi"
    TORNADO = "tornado"

    @classmethod
    def list(cls):
        return [e.value for e in cls]
