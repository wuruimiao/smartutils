import sys
from typing import Dict, Optional

from pydantic import Field

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override


from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory, ConfMeta
from smartutils.config.schema.db import DBConf
from smartutils.config.schema.host import HostConf

__all__ = ["PostgreSQLConf"]


@ConfFactory.register(ConfKey.POSTGRESQL, meta=ConfMeta(multi=True, require=False))
class PostgreSQLConf(DBConf, HostConf):
    port: int = 5432

    timeout: Optional[int] = Field(default=None, alias="connect_timeout", gt=0)
    execute_timeout: Optional[int] = Field(default=None, gt=0)

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.passwd}@{self.host}:{self.port}/{self.db}"

    @property
    @override
    def kw(self) -> Dict:
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
