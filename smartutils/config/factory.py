import sys
from typing import Type, Dict, Tuple

from pydantic import ValidationError

from smartutils.config.const import ConfKey
from smartutils.log import logger

__all__ = ["ConfFactory"]


class ConfFactory:
    _registry: Dict[ConfKey, Tuple[Type, bool, bool]] = {}

    @classmethod
    def register(cls, name: ConfKey, multi: bool = False, require: bool = True):
        def decorator(conf_cls: Type):
            cls._registry[name] = (conf_cls, multi, require)
            return conf_cls

        return decorator

    @classmethod
    def all_keys(cls) -> Tuple:
        return tuple(cls._registry.keys())

    @staticmethod
    def _init_conf_cls(name, key, conf_cls, conf):
        try:
            return conf_cls(**conf)
        except ValidationError as e:
            fields = [err["loc"][0] for err in e.errors()]
            logger.error(
                "ConfFactory {name}-{key} in config.yml miss or invalid fields: {fields}",
                name=name, key=key, fields=fields
            )
            # 非0，k8s判定启动失败；应用在 lifespan 阶段（即启动/关闭事件）报错，uvicorn 退出码是 3
            sys.exit(1)

    @classmethod
    def create(cls, name: ConfKey, conf: Dict):
        info = cls._registry.get(name)
        if not info:
            raise ValueError(f"ConfFactory no conf class registered for {name}")

        conf_cls, multi, require = info
        if not conf:
            if require:
                raise ValueError(f"ConfFactory require {name} in config.yml")
            logger.debug("ConfFactory no {name} in config.yml, ignore.", name=name)
            return

        logger.info("ConfFactory {name} created.", name=name)

        if multi:
            if ConfKey.GROUP_DEFAULT not in conf:
                raise ValueError(f"ConfFactory no {ConfKey.GROUP_DEFAULT} below {name}")

            return {
                key: cls._init_conf_cls(name, key, conf_cls, _conf)
                for key, _conf in conf.items()
            }
        else:
            return cls._init_conf_cls(name, "", conf_cls, conf)

    @classmethod
    def reset(cls):
        cls._registry.clear()
