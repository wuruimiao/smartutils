from enum import Enum
from typing import List

from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory


class MiddlewarePluginKey(str, Enum):
    AUTH = "auth"
    PERMISSION = "permission"
    EXCEPTION = "exception"
    HEADER = "header"
    LOG = "log"


@ConfFactory.register(ConfKey.MIDDLEWARE, multi=False, require=False)
class MiddlewareConf(BaseModel):
    enable: List[MiddlewarePluginKey]
