from pydantic import BaseModel, constr, conint, field_validator

from smartutils.config.const import ConfKeys
from smartutils.config.factory import ConfFactory

from datetime import datetime

from smartutils.time import get_timestamp


@ConfFactory.register(ConfKeys.PROJECT, multi=False, require=True)
class ProjectConf(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    id: conint(ge=0)
    release_time: datetime
    description: constr(strip_whitespace=True, min_length=1) = ""
    version: constr(strip_whitespace=True, min_length=1) = "0.0.1"
    debug: bool = False

    @field_validator("release_time", mode="after")
    def must_be_aware(cls, v):
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError(
                "release_time must be an aware datetime (must contain timezone)"
            )
        return v

    @property
    def release_timestamp_ms(self) -> int:
        return int(get_timestamp(self.release_time)) * 1000
