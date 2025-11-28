from __future__ import annotations

import sys
from typing import Dict, Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.kafka import KafkaConf
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import MQError
from smartutils.infra.mq.cli import AsyncKafkaCli
from smartutils.infra.resource.manager.manager import CTXResourceManager
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override

__all__ = ["KafkaManager"]


@singleton
@CTXVarManager.register(CTXKey.MQ_KAFKA)
class KafkaManager(LibraryCheckMixin, CTXResourceManager[AsyncKafkaCli]):
    def __init__(self, confs: Optional[Dict[str, KafkaConf]] = None):
        self.check(conf=confs)
        assert confs

        resources = {k: AsyncKafkaCli(conf, f"kafka_{k}") for k, conf in confs.items()}
        super().__init__(resources=resources, ctx_key=CTXKey.MQ_KAFKA, error=MQError)

    @property
    @override
    def curr(self) -> AsyncKafkaCli:
        return super().curr


@InitByConfFactory.register(ConfKey.KAFKA)
def _(conf):
    KafkaManager(conf)
