from typing import Dict

from smartutils.config.const import ConfKey, ConfKey
from smartutils.config.schema.mysql import MySQLConf
from smartutils.ctx import CTXVarManager, CTXKey
from smartutils.design import singleton
from smartutils.infra.db.cli import AsyncDBCli, db_commit, db_rollback
from smartutils.infra.factory import InfraFactory
from smartutils.infra.manager import CTXResourceManager


@singleton
@CTXVarManager.register(CTXKey.DB_MYSQL)
class MySQLManager(CTXResourceManager[AsyncDBCli]):
    def __init__(self, confs: Dict[ConfKey, MySQLConf]):
        resources = {k: AsyncDBCli(conf, f"mysql_{k}") for k, conf in confs.items()}
        super().__init__(
            resources, CTXKey.DB_MYSQL, success=db_commit, fail=db_rollback
        )


@InfraFactory.register(ConfKey.MYSQL)
def init_mysql(conf):
    return MySQLManager(conf)
