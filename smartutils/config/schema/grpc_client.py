from typing import Any, List, Optional

from pydantic import BaseModel


class GrpcClientConf(BaseModel):
    endpoint: str
    timeout: Optional[int] = 5
    options: Optional[List[List[Any]]] = []
