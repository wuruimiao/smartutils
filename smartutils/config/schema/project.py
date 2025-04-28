from pydantic import BaseModel, constr

from smartutils.config.const import PROJECT
from smartutils.config.factory import ConfFactory


@ConfFactory.register(PROJECT)
class ProjectConf(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    description: constr(strip_whitespace=True, min_length=1)
    version: constr(strip_whitespace=True, min_length=1)
