from typing import Dict

from smartutils.config.const import ConfKey
from smartutils.config.schema.redis import RedisConf
from smartutils.ctx import CTXVarManager, CTXKey
from smartutils.design import singleton
from smartutils.error.sys import CacheError
from smartutils.infra.cache.cli import AsyncRedisCli
from smartutils.infra.factory import InfraFactory
from smartutils.infra.source_manager.manager import CTXResourceManager

__all__ = ["RedisManager"]


@singleton
@CTXVarManager.register(CTXKey.CACHE_REDIS)
class RedisManager(CTXResourceManager[AsyncRedisCli]):
    def __init__(self, confs: Dict[ConfKey, RedisConf]):
        resources = {k: AsyncRedisCli(conf, f"redis_{k}") for k, conf in confs.items()}
        super().__init__(resources, CTXKey.CACHE_REDIS, error=CacheError)

    @property
    def curr(self) -> AsyncRedisCli:
        return super().curr


@InfraFactory.register(ConfKey.REDIS)
def _(conf):
    return RedisManager(conf)
