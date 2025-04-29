from typing import Type, Dict, Tuple
from smartutils.config.const import CONF_DEFAULT


class ConfFactory:
    _registry: Dict[str, Tuple[Type, bool]] = {}

    @classmethod
    def register(cls, name: str, multi: bool = False):
        def decorator(conf_cls: Type):
            cls._registry[name] = (conf_cls, multi)
            return conf_cls

        return decorator

    @classmethod
    def create(cls, name: str, conf: Dict):
        info = cls._registry.get(name)
        if not info:
            raise ValueError(f"No conf class registered for {name}")

        conf_cls, multi = info
        if multi:
            if CONF_DEFAULT not in conf:
                raise ValueError(f'{CONF_DEFAULT} not in {name}')

            return {key: conf_cls(**_conf) for key, _conf in conf.items()}
        else:
            return conf_cls(**conf)

    @classmethod
    def reset(cls):
        cls._registry.clear()
