from pathlib import Path
from typing import Dict, Any, TypeVar, Optional

import yaml
from smartutils.log import logger
from pydantic import BaseModel

from smartutils.config.const import ConfKeys
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.project import ProjectConf
from smartutils.design import singleton

T = TypeVar("T", bound=BaseModel)


@singleton
class Config:
    def __init__(self, conf_path: str):
        self._instances: Dict[str, T] = {}
        self._config: Dict[str, Any] = {}

        if not Path(conf_path).exists():
            logger.warning(f"Config no {conf_path}, ignore.")
            return

        with open(conf_path) as f:
            self._config = yaml.safe_load(f)

        if not self._config:
            logger.error(f"Config {conf_path} emtpy, ignore.")
            return

        logger.info(f"Config init by {conf_path}.")

        for key in ConfFactory.all_keys():
            self._instances[key] = ConfFactory.create(key, self._config.get(key))

    def get(self, name: str) -> T:
        return self._instances.get(name)

    @property
    def project(self) -> ProjectConf:
        return self.get(ConfKeys.PROJECT)


_config: Optional[Config] = None


def init(conf_path: str = "config/config.yaml") -> Config:
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
