from typing import Optional

from pydantic import field_validator

from smartutils.config.schema.host import HostConf


class RedisConf(HostConf):
    db: int
    port: int = 6379
    passwd: Optional[str] = ""
    timeout: int = 5

    @field_validator('db')
    @classmethod
    def check_db(cls, v):
        if v < 0:
            raise ValueError("Redis db 必须>=0")
        return v

    @field_validator('timeout')
    @classmethod
    def check_timeout(cls, v):
        if v <= 0:
            raise ValueError("timeout必须为正整数")
        return v

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}"