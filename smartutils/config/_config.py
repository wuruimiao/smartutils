from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Type, TypeVar, Union, cast, overload

from pydantic import BaseModel
from typing_extensions import Literal

from smartutils.config.const import BaseModelT, ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.project import ProjectConf
from smartutils.design import MyBase, SingletonMeta
from smartutils.error.sys import ConfigError, LibraryUsageError
from smartutils.file import load_yaml
from smartutils.log import logger

__all__ = ["Config"]


ProjectConfT = TypeVar("ProjectConfT", bound=ProjectConf)
_config: Optional[Config] = None


class Config(MyBase, metaclass=SingletonMeta):
    def __init__(self, conf_path: Optional[str] = None):
        super().__init__()

        assert conf_path, f"{self.name} init need conf_path"

        self._instances: Dict[ConfKey, Union[BaseModel, Dict[str, BaseModel]]] = {}
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
                self._instances[key] = conf

        # 即使配置文件未声明，也要初始化默认ProjectConf
        if ConfKey.PROJECT not in self._instances:
            logger.debug("{} project init default.", self.name)
            self._instances[ConfKey.PROJECT] = ProjectConf()

    def get(self, name: ConfKey) -> Union[BaseModel, Dict[str, BaseModel], None]:
        return self._instances.get(name)

    @overload
    def get_typed(
        self, name: ConfKey, model_cls: Type[BaseModelT], *, expect_dict: Literal[True]
    ) -> Optional[Dict[str, BaseModelT]]: ...
    @overload
    def get_typed(
        self,
        name: ConfKey,
        model_cls: Type[BaseModelT],
        *,
        expect_dict: Literal[False] = False,
    ) -> Optional[BaseModelT]: ...
    def get_typed(
        self, name: ConfKey, model_cls: Type[BaseModelT], *, expect_dict: bool = False
    ):
        val = self.get(name)
        if val is None:
            return None
        if isinstance(val, dict):
            return cast(Dict[str, BaseModelT], val)
        if isinstance(val, model_cls):
            if expect_dict:
                raise LibraryUsageError(
                    f"Value for {name} is not a dict, but expect_dict=True"
                )
            return cast(BaseModelT, val)
        else:  # pragma: no cover
            logger.error(
                "{} value for {} is neither {} nor dict: ",
                self.name,
                name,
                model_cls,
                type(val),
            )
            return None

    @property
    def project(self) -> ProjectConf:
        return self.project_typed(ProjectConf)

    def project_typed(self, model_cls: Type[ProjectConfT]) -> ProjectConfT:
        c = self.get_typed(ConfKey.PROJECT, model_cls)
        assert c is not None
        return c

    @property
    def in_debug(self) -> bool:
        return self.project.debug

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
