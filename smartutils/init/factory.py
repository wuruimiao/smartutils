from typing import Any, Callable

from smartutils.config import Config, ConfKey
from smartutils.config.schema.project import ProjectConf
from smartutils.design import BaseFactory, MyBase
from smartutils.log import logger

__all__ = ["InitByConfFactory"]


class InitByConfFactory(
    MyBase, BaseFactory[ConfKey, Callable[[ProjectConf, Any], Any]]
):
    """
    根据配置初始化组件，包括资源管理器、应用插件等
    若需要其他组件，不需检查其配置，而应该初始化时，尝试从对应的资源管理器获取（有些可能不需配置，或者有配置但是没初始化）。
    """

    # @classmethod
    # def register(cls, key: ConfKey, need_conf: bool = True, **kwargs):  # type: ignore
    #     def decorator(func: Callable[[Any], Any]):
    #         super(InitByConfFactory, cls).register(key, **kwargs)((func, need_conf))
    #         return func

    #     return decorator

    @classmethod
    def init(cls, config: Config):
        # for comp_key, info in cls.all():
        #     init_func, need_conf = info
        for comp_key, init_func in cls.all():
            conf = config.get(comp_key)
            # if need_conf and not conf:
            if not conf:
                logger.debug("{} init by conf no {}, ignore.", cls.name, comp_key)
                continue

            logger.debug("{} init by conf initializing {} ...", cls.name, comp_key)

            init_func(config.project, conf)

            logger.info("{} init by conf {} inited.", cls.name, comp_key)
