from typing import Type, Dict, Tuple

from pydantic import ValidationError

from smartutils.call import exit_on_fail
from smartutils.config.const import ConfKey
from smartutils.design import BaseFactory
from smartutils.error.sys_err import LibraryUsageError
from smartutils.log import logger

__all__ = ["ConfFactory"]


class ConfFactory(BaseFactory[ConfKey, Tuple[Type, bool, bool]]):
    @classmethod
    def register(cls, name: ConfKey, multi: bool = False, require: bool = True):
        def decorator(conf_cls: Type):
            super(ConfFactory, cls).register(name, only_register_once=False)((conf_cls, multi, require))
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
            exit_on_fail()

    @classmethod
    def create(cls, name: ConfKey, conf: Dict):
        info = cls.get(name)

        conf_cls, multi, require = info
        if not conf:
            if require:
                raise LibraryUsageError(f"ConfFactory require {name} in config.yml")
            logger.debug("ConfFactory no {name} in config.yml, ignore.", name=name)
            return

        logger.info("ConfFactory {name} created.", name=name)

        if multi:
            if ConfKey.GROUP_DEFAULT not in conf:
                raise LibraryUsageError(f"ConfFactory no {ConfKey.GROUP_DEFAULT} below {name}")

            return {
                key: cls._init_conf_cls(name, key, conf_cls, _conf)
                for key, _conf in conf.items()
            }
        else:
            return cls._init_conf_cls(name, "", conf_cls, conf)
