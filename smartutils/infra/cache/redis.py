from typing import Dict

from smartutils.config.const import ConfKey, ConfKey
from smartutils.config.schema.redis import RedisConf
from smartutils.ctx import CTXVarManager, CTXKeys
from smartutils.design import singleton
from smartutils.infra.cache.cli import AsyncRedisCli
from smartutils.infra.factory import InfraFactory
from smartutils.infra.manager import CTXResourceManager


@singleton
@CTXVarManager.register(CTXKeys.CACHE_REDIS)
class RedisManager(CTXResourceManager[AsyncRedisCli]):
    def __init__(self, confs: Dict[ConfKey, RedisConf]):
        resources = {k: AsyncRedisCli(conf, f"redis_{k}") for k, conf in confs.items()}
        super().__init__(resources, CTXKeys.CACHE_REDIS)


@InfraFactory.register(ConfKey.REDIS)
def init_redis(conf):
    return RedisManager(conf)
