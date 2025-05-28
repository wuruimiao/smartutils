from contextlib import asynccontextmanager
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from smartutils.config.const import ConfKey
from smartutils.config.schema.mysql import MySQLConf
from smartutils.ctx import CTXVarManager, CTXKey
from smartutils.design import singleton
from smartutils.infra.db.cli import AsyncDBCli, db_commit, db_rollback
from smartutils.infra.factory import InfraFactory
from smartutils.infra.source_manager.manager import CTXResourceManager
from smartutils.error.sys import DatabaseError

__all__ = ["MySQLManager"]


@singleton
@CTXVarManager.register(CTXKey.DB_MYSQL)
class MySQLManager(CTXResourceManager[AsyncDBCli]):
    def __init__(self, confs: Dict[ConfKey, MySQLConf]):
        resources = {k: AsyncDBCli(conf, f"mysql_{k}") for k, conf in confs.items()}
        super().__init__(
            resources, CTXKey.DB_MYSQL, success=db_commit, fail=db_rollback, error=DatabaseError,
        )

    @property
    def curr(self) -> AsyncSession:
        return super().curr

    @asynccontextmanager
    async def session(self, key: ConfKey = ConfKey.GROUP_DEFAULT):
        async with self._resources.get(key).session() as session:
            yield session


@InfraFactory.register(ConfKey.MYSQL)
def _(conf):
    return MySQLManager(conf)
