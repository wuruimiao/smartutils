class CTXKey(str):
    pass


class CTXKeys:
    CACHE_REDIS = CTXKey("cache_redis")

    DB_MYSQL = CTXKey("db_mysql")
    DB_POSTGRESQL = CTXKey("db_postgresql")

    MQ_KAFKA = CTXKey("mq_kafka")

    TRACE_ID = CTXKey("traceid")
    USERID = CTXKey("userid")
    USERNAME = CTXKey("username")

    LOGGER_LOGURU = CTXKey("logger_loguru")

    TIMER = CTXKey("timer")
