from typing import Dict

from smartutils.config.const import REDIS
from smartutils.config.schema.redis import RedisConf
from smartutils.design import singleton
from smartutils.infra.cache.cli import AsyncRedisCli
from smartutils.infra.factory import InfraFactory
from smartutils.infra.manager import ContextResourceManager


@singleton
class RedisManager(ContextResourceManager[AsyncRedisCli]):
    def __init__(self, confs: Dict[str, RedisConf]):
        resources = {k: AsyncRedisCli(conf, f'redis_{k}') for k, conf in confs.items()}
        super().__init__(resources, "cache_redis")


@InfraFactory.register(REDIS)
def init_redis(conf):
    return RedisManager(conf)
