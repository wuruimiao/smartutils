from enum import Enum
from typing import TypeVar

from pydantic import BaseModel

__all__ = ["ConfKey", "BaseModelT"]

BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class ConfKey(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    KAFKA = "kafka"
    CANAL = "canal"

    PROJECT = "project"

    LOGURU = "loguru"

    INSTANCE = "instance"

    OTP = "otp"
    PASSWORD = "password"
    TOKEN = "token"

    OPEN_TELEMETRY = "open_telemetry"

    GROUP_DEFAULT = "default"
