from typing import Literal

from pydantic import BaseModel, Field, constr

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory

__all__ = ["LoguruConfig"]


@ConfFactory.register(ConfKey.LOGURU, multi=False, require=False)
class LoguruConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    rotation: constr(strip_whitespace=True, min_length=1) = Field(
        default="00:00", description="日志轮转条件，如 '10 MB', '1 week', '00:00' 等"
    )
    retention: constr(strip_whitespace=True, min_length=1) = Field(
        default="30 days", description="日志保留时长，如 '30 days'"
    )
    compression: Literal["zip", "gz", "bz2", "xz", "tar"] = "zip"
    logdir: constr(strip_whitespace=True, min_length=1) = None
    enqueue: bool = True
    stream: bool = False
    backtrace: bool = False
    diagnose: bool = False

    @property
    def stream_kw(self) -> dict:
        return self.model_dump(
            exclude={"rotation", "retention", "compression", "logdir", "stream"}
        )

    @property
    def file_kw(self) -> dict:
        return self.model_dump(exclude={"logdir", "stream"})
