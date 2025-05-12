from pydantic import BaseModel, constr

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory

__all__ = ["ProjectConf"]


@ConfFactory.register(ConfKey.PROJECT, multi=False, require=True)
class ProjectConf(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    description: constr(strip_whitespace=True, min_length=1) = ""
    version: constr(strip_whitespace=True, min_length=1) = "0.0.1"
    debug: bool = False
