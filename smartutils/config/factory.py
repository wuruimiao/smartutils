from dataclasses import dataclass
from typing import Dict, Union

from pydantic import BaseModel, ValidationError

from smartutils.config.const import BaseModelT, ConfKey
from smartutils.design import BaseFactory
from smartutils.error.factory import ExcDetailFactory
from smartutils.error.sys import ConfigError
from smartutils.log import logger

__all__ = ["ConfFactory"]


@dataclass
class ConfMeta:
    multi: bool = False  # 是否支持多组配置
    require: bool = False  # 是否必须配置


class ConfFactory(BaseFactory[ConfKey, BaseModelT, ConfMeta]):
    """
    默认不是多组配置，不是必须配置
    """

    # 默认可多次注册同一key
    _default_only_register_once = False

    @classmethod
    def _init_conf_cls(cls, name, key, conf_cls, conf):
        try:
            return conf_cls(**conf)
        except ValidationError as e:
            raise ConfigError(
                f"{cls.name} invalid {name}-{key} in config.yml: {ExcDetailFactory.dispatch(e)}"
            )

    @classmethod
    def create(
        cls, name: ConfKey, conf: Dict
    ) -> Union[BaseModel, Dict[str, BaseModel], None]:
        info = cls.get(name)
        meta = cls.get_meta(name, ConfMeta)

        if not conf:
            # 必需配置
            if meta.require:
                raise ConfigError(f"{cls.name} require {name} in config.yml")
            # 配置文件没声明
            return None

        logger.info("{} {} created.", cls.name, name)

        # 多组配置
        if meta.multi:
            return {
                key: cls._init_conf_cls(name, key, info, _conf)
                for key, _conf in conf.items()
            }
        else:
            return cls._init_conf_cls(name, "", info, conf)
