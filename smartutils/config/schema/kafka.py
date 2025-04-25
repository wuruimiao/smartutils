from typing import List, Literal

from pydantic import BaseModel, field_validator, conlist

from smartutils.config.schema.host import HostConf


class KafkaConf(BaseModel):
    bootstrap_servers: conlist(HostConf, min_length=1)
    client_id: str
    acks: Literal['all', 1, 0] = 'all'
    compression_type: Literal['zstd', 'snappy', None] = None
    max_batch_size: int = 16384
    linger_ms: int = 100
    request_timeout_ms: int = 5000
    retry_backoff_ms: int = 300

    @field_validator('max_batch_size')
    @classmethod
    def batch_size_positive(cls, v):
        if v <= 0:
            raise ValueError('max_batch_size must be positive')
        return v

    @field_validator('linger_ms', 'request_timeout_ms', 'retry_backoff_ms')
    @classmethod
    def must_be_non_negative(cls, v, info):
        if v < 0:
            raise ValueError(f'{info.field_name} must be non-negative')
        return v

    @field_validator('client_id')
    @classmethod
    def client_id_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('client_id must not be empty')
        return v.strip()

    @property
    def urls(self) -> List[str]:
        return [item.the_url for item in self.bootstrap_servers]