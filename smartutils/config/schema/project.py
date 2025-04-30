from pydantic import BaseModel, constr, conint

from smartutils.config.const import ConfKeys
from smartutils.config.factory import ConfFactory


@ConfFactory.register(ConfKeys.PROJECT, multi=False, require=True)
class ProjectConf(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    id: conint(ge=0)
    description: constr(strip_whitespace=True, min_length=1) = ""
    version: constr(strip_whitespace=True, min_length=1) = "0.0.1"
