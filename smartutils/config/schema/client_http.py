from typing import Dict, Optional

from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.breaker import BreakerConf


class HttpApiConf(BaseModel):
    path: str
    method: str = "GET"
    timeout: Optional[int | float] = None


@ConfFactory.register(ConfKey.CLIENT_HTTP, multi=True, require=False)
class ClientHttpConf(BreakerConf):
    endpoint: str
    timeout: int | float = 10
    verify_tls: bool = True
    apis: Optional[Dict[str, HttpApiConf]] = None
