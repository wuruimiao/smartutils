from pydantic import Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.model.field import StrippedBaseModel

__all__ = ["ProjectConf"]


@ConfFactory.register(ConfKey.PROJECT)
class ProjectConf(StrippedBaseModel):
    name: str = Field(default="smartutils-app", min_length=1)
    description: str = Field(default="", min_length=1)
    version: str = Field(default="0.0.1", min_length=1)
    debug: bool = Field(
        default=False,
        description="控制：接口返回detail，服务文档访问，接口返回详细异常内容（已被自定义拦截），腾讯云日志输出",
    )
