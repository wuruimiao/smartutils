class ConfKey(str):
    pass


class ConfKeys:
    MYSQL = ConfKey("mysql")
    POSTGRESQL = ConfKey("postgresql")
    REDIS = ConfKey("redis")
    KAFKA = ConfKey("kafka")
    CANAL = ConfKey("canal")
    PROJECT = ConfKey("project")
    LOGURU = ConfKey("loguru")
    INSTANCE = ConfKey("instance")

    GROUP_DEFAULT = ConfKey("default")
