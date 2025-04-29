from pathlib import Path
from typing import Dict, Any, Optional

import yaml

from smartutils.config.config import ConfigObj
from smartutils.config.factory import ConfFactory
from smartutils.log import logger

_config: ConfigObj


class Config:
    def __init__(self, config_path: str):
        self._instances: Dict[str, Dict[str, Any]] = {}
        self._config: Dict[str, Any] = {}

        if not Path(config_path).exists():
            logger.info(f'conf no {config_path}, do nothing')
            return

        with open(config_path) as f:
            self._config = yaml.safe_load(f)

        if not self._config:
            logger.info(f'conf emtpy, do nothing!!!')
            return

        for key in ConfFactory.all_keys():
            self._instances[key] = ConfFactory.create(key, self._config.get(key))

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        return self._instances.get(name)


def init(conf_path: str = 'config/config.yaml') -> ConfigObj:
    global _config
    _config = ConfigObj(Config(conf_path))
    return _config


def reset():
    global _config
    _config = None


def get_config() -> ConfigObj:
    if _config is None:
        raise RuntimeError("Config not initialized")
    return _config
