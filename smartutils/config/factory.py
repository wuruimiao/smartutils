import sys
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Type, Union

from pydantic import BaseModel, ValidationError

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override


from smartutils.config.const import BaseModelT, ConfKey
from smartutils.design import BaseFactory, MyBase
from smartutils.error.factory import ExcDetailFactory
from smartutils.error.sys import ConfigError
from smartutils.log import logger

__all__ = ["ConfFactory"]


@dataclass
class _ConfMeta:
    conf_cls: Type
    multi: bool
    require: bool


class ConfFactory(MyBase, BaseFactory[ConfKey, _ConfMeta]):
    @override
    @classmethod
    # 屏蔽校验：class定义V为_ConfMeta，BaseFactory.register预期conf_cls也应该是_ConfMeta，但这里需是Type[T]
    # 装饰器模式很难做到类型100%对齐
    def register(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls,
        key: ConfKey,
        only_register_once: bool = False,
        order: Optional[int] = None,
        deps: Optional[List[ConfKey]] = None,
        check_deps: bool = False,
        multi: bool = False,
        require: bool = False,
    ) -> Callable[[Type[BaseModelT]], Type[BaseModelT]]:
        def decorator(conf_cls: Type[BaseModelT]):
            super(ConfFactory, cls).register(key, False, order, deps, check_deps)(
                _ConfMeta(conf_cls, multi, require)
            )
            return conf_cls

        return decorator

    @classmethod
    def _init_conf_cls(cls, name, key, conf_cls, conf):
        try:
            return conf_cls(**conf)
        except ValidationError as e:
            raise ConfigError(
                f"{cls.name} invalid {name}-{key} in config.yml: {ExcDetailFactory.get(e)}"
            )

    @classmethod
    def create(
        cls, name: ConfKey, conf: Dict
    ) -> Union[BaseModel, Dict[str, BaseModel], None]:
        info = cls.get(name)

        if not conf:
            if info.require:
                raise ConfigError(f"{cls.name} require {name} in config.yml")
            # logger.debug(
            #     "{cls_name} no {name} in config.yml, ignore.",
            #     cls_name=cls.name,
            #     name=name,
            # )
            return None

        logger.info("{cls_name} {name} created.", cls_name=cls.name, name=name)

        if info.multi:
            # if ConfKey.GROUP_DEFAULT not in conf:
            #     raise ConfigError(
            #         f"ConfFactory no {ConfKey.GROUP_DEFAULT} below {name}"
            #     )

            return {
                key: cls._init_conf_cls(name, key, info.conf_cls, _conf)
                for key, _conf in conf.items()
            }
        else:
            return cls._init_conf_cls(name, "", info.conf_cls, conf)
