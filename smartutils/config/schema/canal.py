from typing import List

from pydantic import BaseModel, constr

from smartutils.config.const import CANAL
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.host import HostConf


class CanalClientConf(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    client_id: constr(strip_whitespace=True, min_length=1)
    destination: constr(strip_whitespace=True, min_length=1)


@ConfFactory.register(CANAL, multi=True)
class CanalConf(HostConf):
    port: int = 11111
    clients: List[CanalClientConf]
