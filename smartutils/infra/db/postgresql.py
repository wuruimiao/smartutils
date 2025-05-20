from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from smartutils.config.const import ConfKey
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.ctx import CTXVarManager, CTXKey
from smartutils.design import singleton
from smartutils.error.sys import DatabaseError
from smartutils.infra.db.cli import AsyncDBCli, db_commit, db_rollback
from smartutils.infra.factory import InfraFactory
from smartutils.infra.source_manager.manager import CTXResourceManager

__all__ = ["PostgresqlManager"]


@singleton
@CTXVarManager.register(CTXKey.DB_POSTGRESQL)
class PostgresqlManager(CTXResourceManager[AsyncDBCli]):
    def __init__(self, confs: Dict[str, PostgreSQLConf]):
        resources = {
            k: AsyncDBCli(conf, f"postgresql_{k}") for k, conf in confs.items()
        }
        super().__init__(
            resources, CTXKey.DB_POSTGRESQL, success=db_commit, fail=db_rollback, error=DatabaseError,
        )

    @property
    def curr(self) -> AsyncSession:
        return super().curr


@InfraFactory.register(ConfKey.POSTGRESQL)
def _(conf):
    return PostgresqlManager(conf)
