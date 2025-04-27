from typing import Optional

from pydantic import field_validator, Field

from smartutils.config.schema.host import HostConf


class RedisConf(HostConf):
    db: int
    port: int = 6379
    max_connections: int = Field(default=10, alias='pool_size')
    socket_connect_timeout: Optional[int] = Field(default=None, alias='connect_timeout')
    socket_timeout: Optional[int] = None
    password: Optional[str] = Field(default=None, alias='passwd')

    @field_validator('db')
    @classmethod
    def check_db(cls, v):
        if v < 0:
            raise ValueError("Redis db 必须>=0")
        return v

    @field_validator('socket_connect_timeout', 'socket_timeout')
    @classmethod
    def check_timeout_none(cls, v):
        if v is not None and v <= 0:
            raise ValueError("timeout必须为正整数")
        return v

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}"

    @property
    def kw(self) -> dict:
        params = self.model_dump(exclude={'host', 'port'})
        return params
