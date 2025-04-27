from typing import Type, Dict


class ConfFactory:
    registry: Dict[str, Type] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(conf_cls: Type):
            cls.registry[name] = conf_cls
            return conf_cls

        return decorator

    @classmethod
    def create(cls, name: str, conf: dict):
        conf_cls = cls.registry.get(name)
        if not conf_cls:
            raise ValueError(f"No conf class registered for {name}")
        return conf_cls(**conf)
