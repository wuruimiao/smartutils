from typing import Dict, Optional

from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory


class GrpcApiConf(BaseModel):
    stub_class: str
    method: str
    timeout: int = 10


@ConfFactory.register(ConfKey.GRPC_CLIENT, multi=True, require=False)
class GrpcClientConf(BaseModel):
    endpoint: str
    timeout: int = 10
    tls: bool = False
    verify_tls: bool = True
    apis: Optional[Dict[str, GrpcApiConf]] = None
