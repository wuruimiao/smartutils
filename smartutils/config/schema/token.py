from pydantic import BaseModel, constr, conint

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory

__all__ = ["TokenConf"]


@ConfFactory.register(ConfKey.TOKEN, multi=False, require=False)
class TokenConf(BaseModel):
    access_secret: constr(strip_whitespace=True, min_length=1)
    access_exp_min: conint(gt=0)
    refresh_secret: constr(strip_whitespace=True, min_length=1)
    refresh_exp_day: conint(gt=0)
