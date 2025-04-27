import logging
from typing import Dict, Any, Optional

import yaml

from smartutils.design import singleton
from smartutils.config.factory import ConfFactory
from smartutils.config.config import ConfigObj

logger = logging.getLogger(__name__)


@singleton
class Config:
    def __init__(self, config_path: str):
        self._instances: Dict[str, Any] = {}

        with open(config_path) as f:
            self._config: Dict[str, Any] = yaml.safe_load(f)
        for key, conf in self._config.items():
            logger.info(f'load conf: {key}')
            self._instances[key] = ConfFactory.create(key, conf)

    def get(self, name: str) -> Optional[Any]:
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
