from typing import Type, Dict, Tuple

from smartutils.log import logger

from smartutils.config.const import ConfKeys, ConfKey


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

    @classmethod
    def create(cls, name: ConfKey, conf: Dict):
        info = cls._registry.get(name)
        if not info:
            raise ValueError(f"ConfFactory no conf class registered for {name}")

        conf_cls, multi, require = info
        if not conf:
            if require:
                raise ValueError(f"ConfFactory require {name} in config.yml")
            logger.debug(f"ConfFactory no {name} in config.yml, ignore.")
            return

        logger.info(f"{name} created.")

        if multi:
            if ConfKeys.GROUP_DEFAULT not in conf:
                raise ValueError(f"{ConfKeys.GROUP_DEFAULT} not in {name}")

            return {key: conf_cls(**_conf) for key, _conf in conf.items()}
        else:
            return conf_cls(**conf)

    @classmethod
    def reset(cls):
        cls._registry.clear()
