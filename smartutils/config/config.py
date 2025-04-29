from typing import Dict

from smartutils.config.const import ConfKey
from smartutils.config.schema.canal import CanalConf
from smartutils.config.schema.kafka import KafkaConf
from smartutils.config.schema.logger import LoguruConfig
from smartutils.config.schema.mysql import MySQLConf
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.config.schema.project import ProjectConf
from smartutils.config.schema.redis import RedisConf
from smartutils.design import singleton


@singleton
class ConfigObj:
    def __init__(self, config):
        self._config = config

    @property
    def mysql(self) -> Dict[str, MySQLConf]:
        return self._config.get(ConfKey.MYSQL)

    @property
    def postgresql(self) -> Dict[str, PostgreSQLConf]:
        return self._config.get(ConfKey.POSTGRESQL)

    @property
    def redis(self) -> Dict[str, RedisConf]:
        return self._config.get(ConfKey.REDIS)

    @property
    def kafka(self) -> Dict[str, KafkaConf]:
        return self._config.get(ConfKey.KAFKA)

    @property
    def canal(self) -> Dict[str, CanalConf]:
        return self._config.get(ConfKey.CANAL)

    @property
    def project(self) -> ProjectConf:
        return self._config.get(ConfKey.PROJECT)

    @property
    def loguru(self) -> LoguruConfig:
        return self._config.get(ConfKey.LOGURU)
