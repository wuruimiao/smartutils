from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import DatabaseError, LibraryUsageError
from smartutils.infra.db.sqlalchemy_cli import AsyncDBCli, db_commit, db_rollback, msg
from smartutils.infra.factory import InfraFactory
from smartutils.infra.source_manager.manager import CTXResourceManager

try:
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:
    pass
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ["PostgresqlManager"]


@singleton
@CTXVarManager.register(CTXKey.DB_POSTGRESQL)
class PostgresqlManager(CTXResourceManager[AsyncDBCli]):
    def __init__(self, confs: Optional[Dict[ConfKey, PostgreSQLConf]] = None):
        if not confs:
            raise LibraryUsageError("PostgresqlManager must init by infra.")
        assert AsyncSession, msg

        resources = {
            k: AsyncDBCli(conf, f"postgresql_{k}") for k, conf in confs.items()
        }
        super().__init__(
            resources,
            CTXKey.DB_POSTGRESQL,
            success=db_commit,
            fail=db_rollback,
            error=DatabaseError,
        )

    @property
    def curr(self) -> AsyncSession:
        return super().curr[0]


@InfraFactory.register(ConfKey.POSTGRESQL)
def _(conf):
    return PostgresqlManager(conf)
