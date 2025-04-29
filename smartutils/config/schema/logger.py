from typing import Optional, Literal

from pydantic import BaseModel, Field, constr

from smartutils.config.const import LOGURU
from smartutils.config.factory import ConfFactory


@ConfFactory.register(LOGURU)
class LoguruConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    rotation: Optional[constr(strip_whitespace=True, min_length=1)] = Field(
        default="00:00", description="日志轮转条件，如 '10 MB', '1 week', '00:00' 等")
    retention: Optional[constr(strip_whitespace=True, min_length=1)] = Field(
        default="30 days", description="日志保留时长，如 '30 days'")
    compression: Optional[Literal["zip", "gz", "bz2", "xz", "tar"]] = "zip"
    logdir: Optional[constr(strip_whitespace=True, min_length=1)] = None
    enqueue: Optional[bool] = True
    stream: Optional[bool] = False
