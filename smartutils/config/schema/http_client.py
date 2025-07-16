from typing import Dict, Optional

from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory


class HttpApiConf(BaseModel):
    path: str
    method: str = "GET"
    timeout: int = 10


@ConfFactory.register(ConfKey.HTTP_CLIENT, multi=True, require=False)
class HttpClientConf(BaseModel):
    endpoint: str
    timeout: int = 10
    verify_tls: bool = True
    apis: Optional[Dict[str, HttpApiConf]] = None
