from typing import Dict

from smartutils.config.const import ConfKeys, ConfKey
from smartutils.config.schema.mysql import MySQLConf
from smartutils.ctx import CTXVarManager, CTXKeys
from smartutils.design import singleton
from smartutils.infra.db.cli import AsyncDBCli, db_commit, db_rollback
from smartutils.infra.factory import InfraFactory
from smartutils.infra.manager import ContextResourceManager


@singleton
@CTXVarManager.register(CTXKeys.DB_MYSQL)
class MySQLManager(ContextResourceManager[AsyncDBCli]):
    def __init__(self, confs: Dict[ConfKey, MySQLConf]):
        resources = {k: AsyncDBCli(conf, f'mysql_{k}') for k, conf in confs.items()}
        super().__init__(resources, CTXKeys.DB_MYSQL, success=db_commit, fail=db_rollback)


@InfraFactory.register(ConfKeys.MYSQL)
def init_mysql(conf):
    return MySQLManager(conf)
