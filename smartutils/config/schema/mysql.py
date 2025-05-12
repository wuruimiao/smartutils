from pydantic import conint

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.db import DBConf

__all__ = ["MySQLConf"]


@ConfFactory.register(ConfKey.MYSQL, multi=True, require=False)
class MySQLConf(DBConf):
    port: int = 3306

    # 统一单位：秒
    connect_timeout: conint(gt=0) = None
    execute_timeout: conint(gt=0) = None

    @property
    def url(self) -> str:
        return f"mysql+asyncmy://{self.user}:{self.passwd}@{self.host}:{self.port}/{self.db}"

    @property
    def kw(self) -> dict:
        params = super().kw
        params.pop("connect_timeout")
        params.pop("execute_timeout")

        connect_args = {}
        if self.connect_timeout:
            connect_args["connect_timeout"] = self.connect_timeout
        if self.execute_timeout:
            connect_args["init_command"] = (
                f"SET SESSION MAX_EXECUTION_TIME={self.execute_timeout * 1000}"
            )
        if connect_args:
            params["connect_args"] = connect_args
        return params
