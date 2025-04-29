from typing import Type, Dict, Tuple

from smartutils.config.const import ConfKey
from smartutils.log import logger



class ConfFactory:
    _registry: Dict[str, Tuple[Type, bool, bool]] = {}

    @classmethod
    def register(cls, name: str, multi: bool = False, require: bool = True):
        def decorator(conf_cls: Type):
            cls._registry[name] = (conf_cls, multi, require)
            return conf_cls

        return decorator

    @classmethod
    def all_keys(cls) -> Tuple:
        return tuple(cls._registry.keys())

    @classmethod
    def create(cls, name: str, conf: Dict):
        info = cls._registry.get(name)
        if not info:
            raise ValueError(f"No conf class registered for {name}")

        conf_cls, multi, require = info
        if not conf:
            if require:
                raise ValueError(f'must contain {name} in config.yml')
            logger.info(f'conf no key: {name}, ignored.')
            return

        logger.info(f'{name} created.')

        if multi:
            if ConfKey.GROUP_DEFAULT not in conf:
                raise ValueError(f'{ConfKey.GROUP_DEFAULT} not in {name}')

            return {key: conf_cls(**_conf) for key, _conf in conf.items()}
        else:
            return conf_cls(**conf)

    @classmethod
    def reset(cls):
        cls._registry.clear()
