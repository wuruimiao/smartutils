import logging
from typing import Dict, Any, Optional

import yaml

from smartutils.config.schema.canal import CanalConf
from smartutils.config.schema.kafka import KafkaConf
from smartutils.config.schema.mysql import MySQLConf
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.config.schema.redis import RedisConf

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self.mysql: Optional[MySQLConf] = None
        self.redis: Optional[RedisConf] = None
        self.kafka: Optional[KafkaConf] = None
        self.postgresql: Optional[PostgreSQLConf] = None
        self.canal: Optional[CanalConf] = None

        self._map = {
            'mysql': MySQLConf,
            'postgresql': PostgreSQLConf,
            'redis': RedisConf,
            'kafka': KafkaConf,
            'canal': CanalConf,
        }

    def _load_conf(self):
        for key, factory in self._map.items():
            conf = self._config.get(key)
            if not conf:
                continue
            logger.info(f'load conf: {key}')
            setattr(self, key, factory(**conf))

    def load_conf(self, config_path: str):
        with open(config_path) as f:
            self._config = yaml.safe_load(f)

        self._load_conf()


config: Optional[Config]


def init(conf_path: str = 'config/config.yaml'):
    global config
    config = Config()
    config.load_conf(conf_path)
    return True
