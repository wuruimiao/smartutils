from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory


class MiddlewarePluginKey(str, Enum):
    ME = "me"
    PERMISSION = "permission"
    EXCEPTION = "exception"
    HEADER = "header"
    LOG = "log"


class PluginMeConf(BaseModel):
    access_token_name: str = Field(..., description="访问令牌name")


class PluginPermissionConf(BaseModel):
    access_token_name: str = Field(..., description="访问令牌name")


class _MiddlewareConfig(BaseModel):
    me: PluginMeConf = Field(..., description="me插件配置")
    persmission: PluginPermissionConf = Field(..., description="permission插件配置")


@ConfFactory.register(ConfKey.MIDDLEWARE, multi=False, require=False)
class MiddlewareConf(BaseModel):
    app: Optional[List[MiddlewarePluginKey]] = Field(
        None, description="启用的全局中间件"
    )
    routes: Optional[Dict[str, List[MiddlewarePluginKey]]] = Field(
        None, description="启用的路由级别的中间件"
    )
    config: Optional[_MiddlewareConfig] = Field(None, description="中间件配置")
