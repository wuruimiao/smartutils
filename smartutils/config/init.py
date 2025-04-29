from pathlib import Path
from typing import Dict, Any, TypeVar

import yaml
from pydantic import BaseModel

from smartutils.config.factory import ConfFactory
from smartutils.config.schema.project import ProjectConf
from smartutils.config.const import ConfKey
from smartutils.design import singleton
from smartutils.log import logger

T = TypeVar('T', bound=BaseModel)


@singleton
class Config:
    def __init__(self, config_path: str):
        self._instances: Dict[str, T] = {}
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

    def get(self, name: str) -> T:
        return self._instances.get(name)

    @property
    def project(self) -> ProjectConf:
        return self.get(ConfKey.PROJECT)


_config: Config


def init(conf_path: str = 'config/config.yaml') -> Config:
    global _config
    _config = Config(conf_path)
    return _config


def reset():
    global _config
    _config = None


def get_config() -> Config:
    if _config is None:
        raise RuntimeError("Config not initialized")
    return _config
