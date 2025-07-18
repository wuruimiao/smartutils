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
    access_name: str = "access_token"  # 访问令牌name
    client_key: str = "auth"  # 使用配置中client.指向的Client


class PluginPermissionConf(BaseModel):
    access_name: str = "access_token"  # 访问令牌name
    client_key: str = "auth"  # 使用配置中client.指向的Client


class MiddlewarePluginSetting(BaseModel):
    me: PluginMeConf = Field(
        default_factory=lambda: PluginMeConf(), description="me插件配置"
    )
    permission: PluginPermissionConf = Field(
        default_factory=lambda: PluginPermissionConf(), description="permission插件配置"
    )


@ConfFactory.register(ConfKey.MIDDLEWARE, multi=False, require=False)
class MiddlewareConf(BaseModel):
    app: Optional[List[MiddlewarePluginKey]] = Field(
        None, description="启用的全局中间件"
    )
    routes: Optional[Dict[str, List[MiddlewarePluginKey]]] = Field(
        None, description="启用的路由级别的中间件"
    )
    setting: Optional[MiddlewarePluginSetting] = Field(None, description="中间件配置")

    @property
    def safe_setting(self) -> MiddlewarePluginSetting:
        return self.setting or MiddlewarePluginSetting()
