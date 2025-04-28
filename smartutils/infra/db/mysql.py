from typing import Dict

from smartutils.config.const import MYSQL
from smartutils.config.schema.mysql import MySQLConf
from smartutils.design import singleton
from smartutils.infra.db.cli import AsyncDBCli, db_commit, db_rollback
from smartutils.infra.factory import InfraFactory
from smartutils.infra.manager import ContextResourceManager


@singleton
class MySQLManager(ContextResourceManager[AsyncDBCli]):
    def __init__(self, confs: Dict[str, MySQLConf]):
        resources = {k: AsyncDBCli(conf, f'mysql_{k}') for k, conf in confs.items()}
        super().__init__(resources, 'db_mysql', success=db_commit, fail=db_rollback)


@InfraFactory.register(MYSQL)
def init_mysql(conf):
    return MySQLManager(conf)
