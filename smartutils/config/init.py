from pathlib import Path
from typing import Dict, Generic, Optional, TypeVar, Union

from smartutils.config.const import BaseModelT, ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.project import ProjectConf
from smartutils.design import singleton
from smartutils.error.sys import ConfigError, LibraryUsageError
from smartutils.file import load_yaml
from smartutils.log import logger

__all__ = ["Config", "init", "reset", "get_config"]


PT = TypeVar("PT", bound=ProjectConf)


@singleton
class Config(Generic[BaseModelT]):
    def __init__(self, conf_path: str):
        self._instances: Union[
            Dict[str, BaseModelT], Dict[str, Dict[str, BaseModelT]]
        ] = {}
        self._config: Dict[str, Dict] = {}

        if not Path(conf_path).exists():
            logger.warning("Config no {conf_path}, ignore.", conf_path=conf_path)
            return

        self._config = load_yaml(conf_path)

        if not self._config:
            raise ConfigError(f"Config {conf_path} load emtpy, please check it.")

        logger.info("Config init by {conf_path}.", conf_path=conf_path)

        for key, _ in ConfFactory.all():
            conf = ConfFactory.create(key, self._config.get(key, {}))
            if not conf:
                continue
            self._instances[key] = conf  # type: ignore

    def get(self, name: str) -> Union[BaseModelT, Dict[str, BaseModelT], None]:
        return self._instances.get(name)

    @property
    def project(self) -> PT:  # type: ignore
        conf = self.get(ConfKey.PROJECT)
        if not conf:
            raise LibraryUsageError("project must in config.yaml")
        return conf  # type: ignore


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
