from typing import Dict

from smartutils.config.const import ConfKey, ConfKey
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.ctx import CTXVarManager, CTXKeys
from smartutils.design import singleton
from smartutils.infra.db.cli import AsyncDBCli, db_commit, db_rollback
from smartutils.infra.factory import InfraFactory
from smartutils.infra.manager import CTXResourceManager


@singleton
@CTXVarManager.register(CTXKeys.DB_POSTGRESQL)
class PostgresqlManager(CTXResourceManager[AsyncDBCli]):
    def __init__(self, confs: Dict[str, PostgreSQLConf]):
        resources = {
            k: AsyncDBCli(conf, f"postgresql_{k}") for k, conf in confs.items()
        }
        super().__init__(
            resources, CTXKeys.DB_POSTGRESQL, success=db_commit, fail=db_rollback
        )


@InfraFactory.register(ConfKey.POSTGRESQL)
def init_postgresql(conf):
    return PostgresqlManager(conf)
