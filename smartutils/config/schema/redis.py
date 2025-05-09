from typing import Optional

from pydantic import Field, conint, constr

from smartutils.config.const import ConfKeys
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.host import HostConf


@ConfFactory.register(ConfKeys.REDIS, multi=True, require=False)
class RedisConf(HostConf):
    db: conint(ge=0)
    port: int = 6379
    max_connections: int = Field(default=10, alias="pool_size")
    socket_connect_timeout: Optional[conint(gt=0)] = Field(
        default=None, alias="connect_timeout"
    )
    socket_timeout: Optional[conint(gt=0)] = None
    password: Optional[constr(strip_whitespace=True, min_length=1)] = Field(
        default=None, alias="passwd"
    )
    health_check_interval: Optional[conint(gt=0)] = Field(
        default=30, alias="health_check_sec"
    )
    retry_on_timeout: Optional[bool] = True

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}"

    @property
    def kw(self) -> dict:
        params = self.model_dump(exclude={"host", "port"})
        return params
