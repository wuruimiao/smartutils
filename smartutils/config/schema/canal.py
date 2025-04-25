from typing import List, Any

from pydantic import BaseModel, field_validator

from smartutils.config.schema.host import HostConf


class CanalClientConf(BaseModel):
    name: str
    client_id: str
    destination: str

    @field_validator('client_id', 'name', 'destination')
    @classmethod
    def non_empty_str(cls, v, info):
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"{info.field_name} must be non-empty strings")
        return v


class CanalConf(HostConf):
    port: int = 11111
    clients: List[CanalClientConf]
