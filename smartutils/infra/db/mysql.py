from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator, Dict, Optional, Tuple

from smartutils.config.const import ConfKey
from smartutils.config.schema.mysql import MySQLConf
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import DatabaseError, LibraryUsageError
from smartutils.infra.db.sqlalchemy_cli import AsyncDBCli, db_commit, db_rollback, msg
from smartutils.infra.factory import InfraFactory
from smartutils.infra.source_manager.manager import CTXResourceManager

try:
    from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction
except ImportError:
    pass

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

__all__ = ["MySQLManager"]


@singleton
@CTXVarManager.register(CTXKey.DB_MYSQL)
class MySQLManager(CTXResourceManager[AsyncDBCli]):
    def __init__(self, confs: Optional[Dict[ConfKey, MySQLConf]] = None):
        if confs is None:
            raise LibraryUsageError("MySQLManager must init by infra.")
        assert AsyncSession, msg

        resources = {k: AsyncDBCli(conf, f"mysql_{k}") for k, conf in confs.items()}
        super().__init__(
            resources,
            CTXKey.DB_MYSQL,
            success=db_commit,
            fail=db_rollback,
            error=DatabaseError,
        )

    @property
    def curr(self) -> AsyncSession:
        return super().curr[0]

    @asynccontextmanager
    async def session(
        self, key: ConfKey = ConfKey.GROUP_DEFAULT, use_transaction: bool = False
    ) -> AsyncGenerator[Tuple[AsyncSession, Optional[AsyncSessionTransaction]], None]:
        async with self._resources[key].db(use_transaction) as session:
            yield session


@InfraFactory.register(ConfKey.MYSQL)
def _(conf):
    return MySQLManager(conf)
