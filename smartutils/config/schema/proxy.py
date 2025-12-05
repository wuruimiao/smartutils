from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory


@ConfFactory.register(ConfKey.PROXY)
class ProxyConf(BaseModel):
    url: str
