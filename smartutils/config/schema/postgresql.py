from smartutils.config.schema.db import DBConf
from smartutils.config.schema.host import HostConf


class PostgreSQLConf(DBConf, HostConf):
    port: int = 5432

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.passwd}@{self.host}:{self.port}/{self.db}"
