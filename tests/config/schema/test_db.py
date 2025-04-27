import pytest
from pydantic import ValidationError

from smartutils.config.schema.db import DBConf


def valid_conf_dict(**kwargs):
    return {
        'host': 'localhost',
        'port': 3306,
        "user": "root",
        "passwd": "123456",
        "db": "testdb",
        "pool_size": 10,
        "max_overflow": 5,
        "pool_timeout": 30,
        "pool_recycle": 3600,
        "echo": False,
        "echo_pool": False,
        **kwargs
    }


def test_db_con_valid():
    conf = DBConf(**valid_conf_dict())
    assert conf.user == "root"
    assert conf.db == "testdb"
    assert conf.pool_size == 10
    assert conf.max_overflow == 5
    assert conf.pool_timeout == 30
    assert conf.pool_recycle == 3600
    assert conf.echo is False
    assert conf.echo_pool is False


def test_db_con_no_host_port():
    conf_dict = valid_conf_dict()
    conf_dict.pop('host')
    conf_dict.pop('port')
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert '2 validation errors for DBConf' in str(exc.value) and 'host' in str(exc.value) and 'port' in str(
        exc.value)


def test_db_con_default():
    conf = DBConf(host='localhost', port=3306, user="root", passwd='123456', db='testdb')
    assert conf.pool_size == 10
    assert conf.max_overflow == 5
    assert conf.pool_timeout == 10
    assert conf.pool_recycle == 3600
    assert conf.echo is False
    assert conf.echo_pool is False


@pytest.mark.parametrize("field", ["echo", "echo_pool"])
@pytest.mark.parametrize("value", [False, True])
def test_db_con_bool(field, value):
    conf_dict = valid_conf_dict(**{field: value})
    conf = DBConf(**conf_dict)
    assert getattr(conf, field) is value


@pytest.mark.parametrize("field", ["pool_size", "max_overflow", "pool_timeout", "pool_recycle"])
@pytest.mark.parametrize("value", [1, 2, 10, 100])
def test_db_con_int(field, value):
    conf_dict = valid_conf_dict(**{field: value})
    conf = DBConf(**conf_dict)
    assert getattr(conf, field) is value


@pytest.mark.parametrize("field", ["user", "passwd", "db"])
@pytest.mark.parametrize("value", ["", " ", "   "])
def test_db_con_empty_fields(field, value):
    conf_dict = valid_conf_dict(**{field: value})
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert f"{field}不能为空" in str(exc.value)


@pytest.mark.parametrize("field", ["pool_size", "pool_timeout", "pool_recycle"])
@pytest.mark.parametrize("value", [0, -1])
def test_db_con_invalid_pool_size_pool_timeout_pool_recycle(field, value):
    conf_dict = valid_conf_dict(**{field: value})
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert f"{field} 必须大于0" in str(exc.value)


@pytest.mark.parametrize("max_overflow", [-1, -10])
def test_db_con_negative_max_overflow(max_overflow):
    conf_dict = valid_conf_dict(max_overflow=max_overflow)
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert "max_overflow 不能为负数" in str(exc.value)


def test_db_con_kw():
    params = DBConf(**valid_conf_dict()).kw()
    for k in {'user', 'passwd', 'db', 'host', 'port'}:
        assert k not in params
    assert params['pool_size'] == 10
    assert params['max_overflow'] == 5
    assert params['pool_timeout'] == 30
    assert params['pool_recycle'] == 3600
    assert params['echo'] is False
    assert params['echo_pool'] is False
