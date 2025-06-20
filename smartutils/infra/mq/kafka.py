from __future__ import annotations

from typing import Dict, Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.kafka import KafkaConf
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import LibraryUsageError, MQError
from smartutils.infra.factory import InfraFactory
from smartutils.infra.mq.cli import AsyncKafkaCli
from smartutils.infra.source_manager.manager import CTXResourceManager

__all__ = ["KafkaManager"]


@singleton
@CTXVarManager.register(CTXKey.MQ_KAFKA)
class KafkaManager(CTXResourceManager[AsyncKafkaCli]):
    def __init__(self, confs: Optional[Dict[ConfKey, KafkaConf]] = None):
        if not confs:
            raise LibraryUsageError("KafkaManager must init by infra.")

        resources = {k: AsyncKafkaCli(conf, f"kafka_{k}") for k, conf in confs.items()}
        super().__init__(resources, CTXKey.MQ_KAFKA, error=MQError)

    @property
    def curr(self) -> AsyncKafkaCli:
        return super().curr


@InfraFactory.register(ConfKey.KAFKA)
def _(conf):
    return KafkaManager(conf)
