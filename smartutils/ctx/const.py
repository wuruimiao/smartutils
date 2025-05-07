from enum import Enum


class CTXKey(str, Enum):
    CACHE_REDIS = "cache_redis"

    DB_MYSQL = "db_mysql"
    DB_POSTGRESQL = "db_postgresql"

    MQ_KAFKA = "mq_kafka"

    TRACE_ID = "traceid"
    USERID = "userid"
    USERNAME = "username"

    LOGGER_LOGURU = "logger_loguru"

    TIMER = "timer"
