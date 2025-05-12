from typing import List, Literal

from pydantic import BaseModel, conlist, conint, constr

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.host import HostConf

__all__ = ["KafkaConf"]


@ConfFactory.register(ConfKey.KAFKA, multi=True, require=False)
class KafkaConf(BaseModel):
    bootstrap_servers: conlist(HostConf, min_length=1)
    client_id: constr(strip_whitespace=True, min_length=1)
    acks: Literal["all", 1, 0] = "all"
    compression_type: Literal["zstd", "snappy", None] = None
    max_batch_size: conint(gt=0) = 16384
    linger_ms: conint(ge=0) = 0
    request_timeout_ms: conint(gt=0) = 40000
    retry_backoff_ms: conint(gt=0) = 100

    @property
    def urls(self) -> List[str]:
        return [item.the_url for item in self.bootstrap_servers]

    @property
    def kw(self) -> dict:
        params = self.model_dump(exclude={"bootstrap_servers"})
        return params
