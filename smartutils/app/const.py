import sys
from enum import Enum, IntEnum

__all__ = [
    "HeaderKey",
    "AppKey",
    "MiddlewarePluginKey",
    "MiddlewarePluginOrder",
    "CONF_ENV_NAME",
]


class HeaderKey(str, Enum):
    X_USER_ID = "X-User-Id"
    X_USER_NAME = "X-User-Name"
    X_TRACE_ID = "X-Trace-ID"
    X_P_USER_IDS = "X-P-User-Ids"


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


class MiddlewarePluginKey(Enum):
    EXCEPTION = "exception"
    HEADER = "header"
    LOG = "log"


class MiddlewarePluginOrder(IntEnum):
    EXCEPTION = -sys.maxsize
    HEADER = sys.maxsize
    LOG = 1


CONF_ENV_NAME = "smartutils_conf_path"
