import logging
from typing import Dict, Any, Optional

import yaml

from smartutils.config.config import ConfigObj
from smartutils.config.const import CONF_DEFAULT, PROJECT
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.project import ProjectConf

logger = logging.getLogger(__name__)

__all__ = ['Config', 'init', 'get_config', 'ConfFactory', 'PROJECT', 'ProjectConf']


class Config:
    def __init__(self, config_path: str):
        self._instances: Dict[str, Dict[str, Any]] = {}
        self._config: Dict[str, Any] = {}

        with open(config_path) as f:
            self._config = yaml.safe_load(f)

        if not self._config:
            logger.info(f'conf emtpy, do nothing!!!')
            return

        for key, conf in self._config.items():
            logger.info(f'load conf: {key}')
            self._instances[key] = ConfFactory.create(key, conf)

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        return self._instances.get(name)


_config: ConfigObj


def init(conf_path: str = 'config/config.yaml') -> ConfigObj:
    global _config
    _config = ConfigObj(Config(conf_path))
    return _config


def get_config() -> ConfigObj:
    global _config
    if _config is None:
        raise RuntimeError("Config not initialized")
    return _config
