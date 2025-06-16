from pydantic import BaseModel, Field

from smartutils.config.schema.host import HostConf

__all__ = ["DBConf"]


class PoolConf(BaseModel):
    pool_size: int = Field(10, gt=0)
    max_overflow: int = Field(5, ge=0)
    pool_timeout: int = Field(
        10,
        gt=0,
        description="当连接池没有可用连接时，等待连接回收的最长时间（秒）",
    )
    pool_recycle: int = Field(
        3600,
        gt=0,
        description="连接池中连接的最大回收时间（秒）。到达时间后，不同库的行为参考库，如sqlalchemy关闭并重新创建",
    )

    def max_pool_size(self) -> int:
        return self.pool_size + self.max_overflow

    def min_pool_size(self) -> int:
        return self.pool_size


class DBConf(HostConf, PoolConf):
    user: str = Field(..., min_length=1, description="用户名")
    passwd: str = Field(..., min_length=1, description="密码")
    db: str = Field(..., min_length=1, description="库")

    echo: bool = False
    echo_pool: bool = False

    @property
    def kw(self) -> dict:
        params = self.model_dump(exclude={"user", "passwd", "db", "host", "port"})
        return params
