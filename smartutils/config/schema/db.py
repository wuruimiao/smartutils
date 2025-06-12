from pydantic import Field

from smartutils.config.schema.host import HostConf

__all__ = ["DBConf"]


class DBConf(HostConf):
    user: str = Field(..., min_length=1, description="用户名")
    passwd: str = Field(..., min_length=1, description="密码")
    db: str = Field(..., min_length=1, description="库")

    pool_size: int = Field(10, gt=0)
    max_overflow: int = Field(5, ge=0)
    pool_timeout: int = Field(10, gt=0)
    pool_recycle: int = Field(3600, gt=0)
    echo: bool = False
    echo_pool: bool = False

    @property
    def kw(self) -> dict:
        params = self.model_dump(exclude={"user", "passwd", "db", "host", "port"})
        return params
