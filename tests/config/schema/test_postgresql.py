import pytest
from pydantic import ValidationError

from smartutils.config.schema.postgresql import PostgreSQLConf


def valid_conf_dict(**kwargs):
    # 构造一份合法的 PostgreSQLConf 配置
    base = {
        "user": "pguser",
        "passwd": "pgpass",
        "db": "mydb",
        "host": "127.0.0.1",
        # "port": 5432,  # 可省略，默认5432
        **kwargs
    }
    return base


def test_postgresql_conf_url_default_port():
    conf = PostgreSQLConf(**valid_conf_dict())
    assert conf.port == 5432
    # 检查 URL 构造
    assert conf.url == "postgresql+asyncpg://pguser:pgpass@127.0.0.1:5432/mydb"


def test_postgresql_conf_url_custom_port():
    conf = PostgreSQLConf(**valid_conf_dict(port=5433))
    assert conf.port == 5433
    assert conf.url == "postgresql+asyncpg://pguser:pgpass@127.0.0.1:5433/mydb"


@pytest.mark.parametrize("user", ["", None, "   "])
def test_postgresql_conf_invalid_user(user):
    with pytest.raises(ValidationError):
        PostgreSQLConf(**valid_conf_dict(user=user))


@pytest.mark.parametrize("host", ["", None, "not_a_host", "256.256.256.256"])
def test_postgresql_conf_invalid_host(host):
    with pytest.raises(ValidationError):
        PostgreSQLConf(**valid_conf_dict(host=host))


@pytest.mark.parametrize("port", [0, 70000, -1])
def test_postgresql_conf_invalid_port(port):
    with pytest.raises(ValidationError):
        PostgreSQLConf(**valid_conf_dict(port=port))


@pytest.mark.parametrize("db", ["", None, "   "])
def test_postgresql_conf_invalid_db(db):
    with pytest.raises(ValidationError):
        PostgreSQLConf(**valid_conf_dict(db=db))

# 你可以根据 DBConf/HostConf 校验项继续补充异常case
