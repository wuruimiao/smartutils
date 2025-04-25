from typing import Optional

from pydantic import BaseModel

from smartutils.config.schema.db import DBConf
from smartutils.config.schema.host import HostConf


class ConnectArgsConfig(BaseModel):
    connect_timeout: Optional[int] = 10


class EngineOptionsConfig(BaseModel):
    port: int = 3306
    echo: Optional[bool] = False
    future: Optional[bool] = True
    connect_args: Optional[ConnectArgsConfig] = ConnectArgsConfig()


class MySQLConf(DBConf, HostConf):
    port: int = 3306
    engine_options: EngineOptionsConfig = EngineOptionsConfig()

    @property
    def url(self) -> str:
        return f"mysql+asyncmy://{self.user}:{self.passwd}@{self.host}:{self.port}/{self.db}"
