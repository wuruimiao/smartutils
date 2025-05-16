from enum import Enum

__all__ = ["ConfKey"]


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
