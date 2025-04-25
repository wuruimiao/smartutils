from pydantic import BaseModel, field_validator, model_validator


class DBConf(BaseModel):
    user: str
    passwd: str
    db: str

    pool_size: int = 10
    max_overflow: int = 5
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    echo_pool: bool = False
    pool_pre_ping: bool = True
    pool_reset_on_return: str = 'rollback'

    @field_validator('user', 'passwd', 'db')
    @classmethod
    def check_not_empty(cls, v, info):
        if not v or not str(v).strip():
            raise ValueError(f"{info.field_name}不能为空")
        return v

    @field_validator('pool_size')
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

    @field_validator('pool_reset_on_return')
    @classmethod
    def check_pool_reset_on_return(cls, v):
        if v != 'rollback':
            raise ValueError("pool_reset_on_return 只能为 'rollback'，不允许在配置文件覆盖！")
        return v

    @field_validator('pool_pre_ping')
    @classmethod
    def check_pool_pre_ping(cls, v):
        if not v:
            raise ValueError("pool_pre_ping只能为 'true'，不允许在配置文件覆盖！")
        return v

    @model_validator(mode='after')
    def check_all(self):
        return self
