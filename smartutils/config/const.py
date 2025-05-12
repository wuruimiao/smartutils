from enum import Enum


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

    GROUP_DEFAULT = "default"
