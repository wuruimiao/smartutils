from pydantic import field_validator

from smartutils.config.schema.host import HostConf


class DBConf(HostConf):
    user: str
    passwd: str
    db: str

    pool_size: int = 10
    max_overflow: int = 5
    pool_timeout: int = 10
    pool_recycle: int = 3600
    echo: bool = False
    echo_pool: bool = False

    @field_validator('user', 'passwd', 'db')
    @classmethod
    def check_not_empty(cls, v, info):
        if not v or not str(v).strip():
            raise ValueError(f"{info.field_name}不能为空")
        return v

    @field_validator('pool_size', 'pool_timeout', 'pool_recycle')
    @classmethod
    def check_positive(cls, v, info):
        if v < 1:
            raise ValueError(f'{info.field_name} 必须大于0')
        return v

    @field_validator('max_overflow')
    @classmethod
    def check_non_negative(cls, v, info):
        if v < 0:
            raise ValueError(f'{info.field_name} 不能为负数')
        return v

    @property
    def kw(self) -> dict:
        params = self.model_dump(exclude={'user', 'passwd', 'db', 'host', 'port'})
        return params
