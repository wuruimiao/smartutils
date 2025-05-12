from pydantic import conint, constr

from smartutils.config.schema.host import HostConf

__all__ = ["DBConf"]


class DBConf(HostConf):
    user: constr(strip_whitespace=True, min_length=1)
    passwd: constr(strip_whitespace=True, min_length=1)
    db: constr(strip_whitespace=True, min_length=1)

    pool_size: conint(gt=0) = 10
    max_overflow: conint(ge=0) = 5
    pool_timeout: conint(gt=0) = 10
    pool_recycle: conint(gt=0) = 3600
    echo: bool = False
    echo_pool: bool = False

    @property
    def kw(self) -> dict:
        params = self.model_dump(exclude={"user", "passwd", "db", "host", "port"})
        return params
