from smartutils.config.const import MYSQL, POSTGRESQL, REDIS, KAFKA, CANAL
from smartutils.config.schema.canal import CanalConf
from smartutils.config.schema.kafka import KafkaConf
from smartutils.config.schema.mysql import MySQLConf
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.config.schema.redis import RedisConf
from smartutils.design import singleton


@singleton
class ConfigObj:
    def __init__(self, config):
        self._config = config

    @property
    def mysql(self) -> MySQLConf:
        return self._config.get(MYSQL)

    @property
    def postgresql(self) -> PostgreSQLConf:
        return self._config.get(POSTGRESQL)

    @property
    def db(self) -> MySQLConf | PostgreSQLConf | None:
        if self.mysql:
            return self.mysql
        if self.postgresql:
            return self.postgresql
        return None

    @property
    def cache(self) -> RedisConf:
        return self._config.get(REDIS)

    @property
    def mq(self) -> KafkaConf:
        return self._config.get(KAFKA)

    @property
    def canal(self) -> CanalConf:
        return self._config.get(CANAL)
