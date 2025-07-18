from typing import Any, Callable

from smartutils.call import call_hook
from smartutils.config import Config, ConfKey
from smartutils.design import BaseFactory
from smartutils.log import logger

__all__ = ["InitByConfFactory"]


class InitByConfFactory(BaseFactory[ConfKey, Callable[[Any], Any]]):
    # @classmethod
    # def register(cls, key: ConfKey, need_conf: bool = True, **kwargs):  # type: ignore
    #     def decorator(func: Callable[[Any], Any]):
    #         super(InitByConfFactory, cls).register(key, **kwargs)((func, need_conf))
    #         return func

    #     return decorator

    @classmethod
    async def init(cls, config: Config):
        # for comp_key, info in cls.all():
        #     init_func, need_conf = info
        for comp_key, init_func in cls.all():
            conf = config.get(comp_key)
            # if need_conf and not conf:
            if not conf:
                logger.debug(
                    "infra init config no {comp_key}, ignore.", comp_key=comp_key
                )
                continue

            logger.debug("infra initializing {comp_key} ...", comp_key=comp_key)

            await call_hook(init_func, conf)

            logger.info("infra {comp_key} inited.", comp_key=comp_key)
