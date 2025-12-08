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
    # 即使配置文件未声明，也自动初始化默认配置。常用于ProjectConf；
    # 注意：若配置同时关联了InitByConfFactory，建议不要开启。由组件定义没有配置时的初始化行为，用到时再初始化。
    # 如：MiddlewareConf
    auto_init: bool = False


class ConfFactory(BaseFactory[ConfKey, BaseModelT, ConfMeta]):
    """
    管理：不同配置项，如何构造对应的配置类实例。
    支持多组配置和可选配置，方便灵活地管理应用配置。
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
            if not meta.auto_init:
                # 配置文件没声明
                return None
            else:
                logger.debug("{} {} init default.", cls.name, name)

        logger.debug("{} {} created.", cls.name, name)

        # 多组配置
        if meta.multi:
            return {
                key: cls._init_conf_cls(name, key, info, _conf)
                for key, _conf in conf.items()
            }
        else:
            return cls._init_conf_cls(name, "", info, conf)
