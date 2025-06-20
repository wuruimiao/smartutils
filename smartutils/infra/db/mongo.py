from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator, Dict, Optional, Tuple

from smartutils.config.const import ConfKey
from smartutils.config.schema.mongo import MongoConf
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import DatabaseError, LibraryUsageError
from smartutils.infra.db.mongo_cli import AsyncMongoCli, db_commit, db_rollback, msg
from smartutils.infra.factory import InfraFactory
from smartutils.infra.source_manager.manager import CTXResourceManager

try:
    from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorDatabase
except ImportError:
    pass

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorDatabase

__all__ = ["MongoManager"]


@singleton
@CTXVarManager.register(CTXKey.DB_MONGO)
class MongoManager(CTXResourceManager[AsyncMongoCli]):
    def __init__(self, confs: Optional[Dict[ConfKey, MongoConf]] = None):
        if confs is None:
            raise LibraryUsageError("MongoManager must init by infra.")
        assert AsyncIOMotorDatabase, msg
        resources = {k: AsyncMongoCli(conf, f"mongo_{k}") for k, conf in confs.items()}
        super().__init__(
            resources,
            CTXKey.DB_MONGO,
            success=db_commit,
            fail=db_rollback,
            error=DatabaseError,
        )

    @property
    def curr(self) -> AsyncIOMotorDatabase:
        return super().curr[0]

    @property
    def curr_session(self) -> AsyncIOMotorClientSession:
        return super().curr[1]

    @asynccontextmanager
    async def session(
        self, key: ConfKey = ConfKey.GROUP_DEFAULT, use_transaction: bool = False
    ) -> AsyncGenerator[
        Tuple[AsyncIOMotorDatabase, Optional[AsyncIOMotorClientSession]], None
    ]:
        async with self._resources[key].db(use_transaction) as session:
            yield session


@InfraFactory.register(ConfKey.MONGO)
def _(conf):
    return MongoManager(conf)
