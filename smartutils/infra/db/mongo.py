from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Dict, Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.mongo import MongoConf
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import SingletonMeta
from smartutils.error.sys import DatabaseError
from smartutils.infra.db.mongo_cli import AsyncMongoCli, db_commit, db_rollback
from smartutils.infra.resource.manager.manager import CTXResourceManager
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override

try:
    from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorDatabase
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorDatabase

__all__ = ["MongoManager"]


CTXVarManager.register_v(CTXKey.DB_MONGO)


class MongoManager(
    LibraryCheckMixin, CTXResourceManager[AsyncMongoCli], metaclass=SingletonMeta
):
    def __init__(self, confs: Optional[Dict[str, MongoConf]] = None):
        self.check(conf=confs)
        assert confs

        resources = {k: AsyncMongoCli(conf, f"mongo_{k}") for k, conf in confs.items()}
        super().__init__(
            resources=resources,
            ctx_key=CTXKey.DB_MONGO,
            success=db_commit,
            fail=db_rollback,
            error=DatabaseError,
        )

    # 屏蔽校验：DB返回值不是资源实例本身
    @property
    @override
    def curr(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> AsyncIOMotorDatabase:
        return super().curr[0]  # pyright: ignore[reportIndexIssue]

    @property
    def curr_session(self) -> AsyncIOMotorClientSession:
        return super().curr[1]  # pyright: ignore[reportIndexIssue]

    # @asynccontextmanager
    # async def session(
    #     self, key: ConfKey = ConfKey.GROUP_DEFAULT, use_transaction: bool = False
    # ) -> AsyncGenerator[
    #     Tuple[AsyncIOMotorDatabase, Optional[AsyncIOMotorClientSession]], None
    # ]:
    #     async with self._resources[key].db(use_transaction) as session:
    #         yield session


@InitByConfFactory.register(ConfKey.MONGO)
def _(_, conf):
    return MongoManager(conf)
