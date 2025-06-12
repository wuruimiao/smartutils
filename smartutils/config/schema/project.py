from pydantic import Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.model.field import StrippedBaseModel

__all__ = ["ProjectConf"]


@ConfFactory.register(ConfKey.PROJECT, multi=False, require=True)
class ProjectConf(StrippedBaseModel):
    name: str = Field(min_length=1)
    description: str = Field("", min_length=1)
    version: str = Field("0.0.1", min_length=1)
    debug: bool = False
