from pydantic import Field, conint

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.db import DBConf
from smartutils.config.schema.host import HostConf

__all__ = ["PostgreSQLConf"]


@ConfFactory.register(ConfKey.POSTGRESQL, multi=True, require=False)
class PostgreSQLConf(DBConf, HostConf):
    port: int = 5432

    timeout: conint(gt=0) = Field(default=None, alias="connect_timeout")
    execute_timeout: conint(gt=0) = None

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.passwd}@{self.host}:{self.port}/{self.db}"

    @property
    def kw(self) -> dict:
        params = super().kw
        for k in {"timeout", "execute_timeout"}:
            params.pop(k)
        connect_args = {}
        if self.timeout:
            connect_args["timeout"] = self.timeout

        if self.execute_timeout:
            connect_args["server_settings"] = {
                "statement_timeout": f"{self.execute_timeout * 1000}"
            }

        if connect_args:
            params["connect_args"] = connect_args
        return params
