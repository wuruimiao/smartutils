from typing import Dict

from smartutils.config.const import ConfKey
from smartutils.config.schema.kafka import KafkaConf
from smartutils.ctx import ContextVarManager, CTXKey
from smartutils.design import singleton
from smartutils.infra.factory import InfraFactory
from smartutils.infra.manager import ContextResourceManager
from smartutils.infra.mq.cli import AsyncKafkaCli


@singleton
@ContextVarManager.register(CTXKey.MQ_KAFKA)
class KafkaManager(ContextResourceManager[AsyncKafkaCli]):
    def __init__(self, confs: Dict[str, KafkaConf]):
        resources = {k: AsyncKafkaCli(conf, f'kafka_{k}') for k, conf in confs.items()}
        super().__init__(resources, CTXKey.MQ_KAFKA)


@InfraFactory.register(ConfKey.KAFKA)
def init_kafka(conf):
    return KafkaManager(conf)
