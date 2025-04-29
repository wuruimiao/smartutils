from typing import Dict

from smartutils.config.const import KAFKA
from smartutils.config.schema.kafka import KafkaConf
from smartutils.ctx import ContextVarManager, CTX_MQ_KAFKA
from smartutils.design import singleton
from smartutils.infra.factory import InfraFactory
from smartutils.infra.manager import ContextResourceManager
from smartutils.infra.mq.cli import AsyncKafkaCli


@singleton
@ContextVarManager.register(CTX_MQ_KAFKA)
class KafkaManager(ContextResourceManager[AsyncKafkaCli]):
    def __init__(self, confs: Dict[str, KafkaConf]):
        resources = {k: AsyncKafkaCli(conf, f'kafka_{k}') for k, conf in confs.items()}
        super().__init__(resources, CTX_MQ_KAFKA)


@InfraFactory.register(KAFKA)
def init_kafka(conf):
    return KafkaManager(conf)
