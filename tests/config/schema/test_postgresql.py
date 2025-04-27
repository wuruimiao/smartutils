import pytest
from pydantic import ValidationError

from smartutils.config.schema.postgresql import PostgreSQLConf


def valid_conf_dict(**kwargs):
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


def test_postgresql_conf_kw():
    conf = PostgreSQLConf(**valid_conf_dict())
    params = conf.kw
    for k in {'host', 'port', 'user', 'passwd', 'db'}:
        assert k not in params
    assert params['pool_size'] == 10
    assert params['max_overflow'] == 5
    assert params['pool_timeout'] == 10
    assert params['pool_recycle'] == 3600
    assert params['echo'] is False
    assert params['echo_pool'] is False
    assert 'connect_args' not in params


@pytest.mark.parametrize("value", [1, 2, 3, 10])
def test_postgresql_conf_kw_connect_timeout(value):
    conf_dict = valid_conf_dict()
    conf_dict['connect_timeout'] = value
    params = PostgreSQLConf(**conf_dict).kw
    assert 'connect_args' in params
    assert params['connect_args']['timeout'] == value


@pytest.mark.parametrize("value", [1, 2, 3, 10])
def test_postgresql_conf_kw_execute_timeout(value):
    conf_dict = valid_conf_dict()
    conf_dict['execute_timeout'] = value
    params = PostgreSQLConf(**conf_dict).kw
    assert 'connect_args' in params
    assert params['connect_args']['server_settings']['statement_timeout'] == f'{value * 1000}'
