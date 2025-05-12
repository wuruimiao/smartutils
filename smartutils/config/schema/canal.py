from typing import List

from pydantic import BaseModel, constr

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.host import HostConf

__all__ = ["CanalClientConf", "CanalConf"]


class CanalClientConf(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    client_id: constr(strip_whitespace=True, min_length=1)
    destination: constr(strip_whitespace=True, min_length=1)


@ConfFactory.register(ConfKey.CANAL, multi=True, require=False)
class CanalConf(HostConf):
    port: int = 11111
    clients: List[CanalClientConf]
