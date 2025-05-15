from pathlib import Path
from typing import Dict, Any, TypeVar, Optional

from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.project import ProjectConf
from smartutils.design import singleton
from smartutils.error.sys import ConfigError, LibraryUsageError
from smartutils.file import load_yaml
from smartutils.log import logger

__all__ = ["Config", "init", "reset", "get_config"]

T = TypeVar("T", bound=BaseModel)

PT = TypeVar("PT", bound=ProjectConf)


@singleton
class Config:
    def __init__(self, conf_path: str):
        self._instances: Dict[str, T] = {}
        self._config: Dict[str, Any] = {}

        if not Path(conf_path).exists():
            logger.warning("Config no {conf_path}, ignore.", conf_path=conf_path)
            return

        self._config = load_yaml(conf_path)

        if not self._config:
            raise ConfigError(f"Config {conf_path} load emtpy, please check it.")

        logger.info("Config init by {conf_path}.", conf_path=conf_path)

        for key, _ in ConfFactory.all():
            self._instances[key] = ConfFactory.create(key, self._config.get(key))

    def get(self, name: str) -> T:
        return self._instances.get(name)

    @property
    def project(self) -> PT:
        return self.get(ConfKey.PROJECT)


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
        raise LibraryUsageError("Config not initialized")
    return _config
