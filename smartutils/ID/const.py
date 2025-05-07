from enum import Enum


class IDGenType(Enum):
    SNOWFLAKE = "snowflake"
    UUID = "uuid"
    ULID = "ulid"
