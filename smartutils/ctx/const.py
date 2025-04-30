class CTXKey(str):
    pass


class CTXKeys:
    CACHE_REDIS = CTXKey('cache_redis')

    DB_MYSQL = CTXKey('db_mysql')
    DB_POSTGRESQL = CTXKey('db_postgresql')

    MQ_KAFKA = CTXKey('mq_kafka')

    TRACE_ID = CTXKey('traceid')
    USERID = CTXKey('userid')
    USERNAME = CTXKey('username')

    NO_USE = CTXKey('no_use')
