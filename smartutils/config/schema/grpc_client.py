from typing import Dict, Optional

from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.breaker import BreakerConf


class GrpcApiConf(BaseModel):
    stub_class: str
    method: str
    timeout: Optional[int | float] = None


@ConfFactory.register(ConfKey.GRPC_CLIENT, multi=True, require=False)
class GrpcClientConf(BreakerConf):
    endpoint: str
    timeout: int | float = 10
    tls: bool = False
    verify_tls: bool = True
    apis: Optional[Dict[str, GrpcApiConf]] = None
