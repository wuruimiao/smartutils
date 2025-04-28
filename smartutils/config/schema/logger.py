import os
from typing import Optional, Literal

from pydantic import BaseModel, Field, constr, model_validator

from smartutils.config.factory import ConfFactory
from smartutils.config.const import LOGURU


@ConfFactory.register(LOGURU)
class LoguruConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Optional[constr(strip_whitespace=True, min_length=1)] = \
        ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
         "<level>{level: <8}</level> | "
         "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    rotation: Optional[constr(strip_whitespace=True, min_length=1)] = Field(
        default="00:00", description="日志轮转条件，如 '10 MB', '1 week', '00:00' 等")
    retention: Optional[constr(strip_whitespace=True, min_length=1)] = Field(
        default="30 days", description="日志保留时长，如 '30 days'")
    compression: Optional[Literal["zip", "gz", "bz2", "xz", "tar"]] = "zip"
    logfile: Optional[constr(strip_whitespace=True, min_length=1)] = None
    enqueue: bool = Field(default=True)

    @model_validator(mode="after")
    def check_logfile_dir(self):
        if self.logfile:
            parent = os.path.dirname(self.logfile)
            if parent and not os.path.exists(parent):
                raise ValueError(f"logfile parent dir not exist: {parent}")
        return self
