from __future__ import annotations

from pathlib import Path
from typing import Dict, Generic, Optional, TypeVar, Union

from smartutils.config.const import ConfKey, TBaseModel
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.project import ProjectConf
from smartutils.design import MyBase, SingletonMeta
from smartutils.error.sys import ConfigError, LibraryUsageError
from smartutils.file import load_yaml
from smartutils.log import logger

__all__ = ["Config"]


TProject = TypeVar("TProject", bound=ProjectConf)
_config: Optional[Config] = None


class Config(MyBase, Generic[TBaseModel], metaclass=SingletonMeta):
    def __init__(self, conf_path: str):
        self._instances: Union[
            Dict[str, TBaseModel], Dict[str, Dict[str, TBaseModel]]
        ] = {}
        self._config: Dict[str, Dict] = {}

        if not Path(conf_path).exists():
            logger.warning(
                "{name} no {conf_path}, ignore.", name=self.name, conf_path=conf_path
            )
        else:

            self._config = load_yaml(conf_path)

            if not self._config:
                raise ConfigError(
                    f"{self.name} {conf_path} load emtpy, please check it."
                )

            logger.info(
                "{name} init by {conf_path}.", name=self.name, conf_path=conf_path
            )

            for key, _ in ConfFactory.all():
                conf = ConfFactory.create(key, self._config.get(key, {}))
                if not conf:
                    continue
                self._instances[key] = conf  # type: ignore

        if ConfKey.PROJECT not in self._instances:
            logger.debug("{name} project init default.", name=self.name)
            self._instances[ConfKey.PROJECT] = ProjectConf()

    def get(self, name: str) -> Union[TBaseModel, Dict[str, TBaseModel], None]:
        return self._instances.get(name)

    @property
    def project(self) -> TProject:  # type: ignore
        return self._instances[ConfKey.PROJECT]  # type: ignore

    @classmethod
    def init(cls, conf_path: str) -> Config:
        global _config
        _config = Config(conf_path)
        return _config

    @classmethod
    def reset(cls):
        global _config
        _config = None

    @classmethod
    def get_config(cls) -> Config:
        if _config is None:
            raise LibraryUsageError(f"{cls.name} not initialized")
        return _config
