import pytest
from pydantic import ValidationError

from smartutils.config.schema.db import DBConf


def valid_conf_dict(**kwargs):
    return {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "passwd": "123456",
        "db": "testdb",
        "pool_size": 10,
        "max_overflow": 5,
        "pool_timeout": 30,
        "pool_recycle": 3600,
        "echo": False,
        "echo_pool": False,
        **kwargs,
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
    conf_dict.pop("host")
    conf_dict.pop("port")
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert (
        "2 validation errors for DBConf" in str(exc.value)
        and "host" in str(exc.value)
        and "port" in str(exc.value)
    )


def test_db_con_default():
    conf = DBConf(
        host="localhost", port=3306, user="root", passwd="123456", db="testdb"
    )
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


@pytest.mark.parametrize(
    "field", ["pool_size", "max_overflow", "pool_timeout", "pool_recycle"]
)
@pytest.mark.parametrize("value", [1, 2, 10, 100])
def test_db_con_int(field, value):
    conf_dict = valid_conf_dict(**{field: value})
    conf = DBConf(**conf_dict)
    assert getattr(conf, field) is value


@pytest.mark.parametrize("field", ["user", "passwd", "db"])
@pytest.mark.parametrize("value", ["", " ", "   "])
def test_db_con_empty(field, value):
    conf_dict = valid_conf_dict(**{field: value})
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert "String should have at least 1 character" in str(exc.value) and field in str(
        exc.value
    )


@pytest.mark.parametrize("field", ["pool_size", "pool_timeout", "pool_recycle"])
@pytest.mark.parametrize("value", [0, -1])
def test_db_con_gt_0(field, value):
    conf_dict = valid_conf_dict(**{field: value})
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert "Input should be greater than 0" in str(exc.value) and field in str(
        exc.value
    )


@pytest.mark.parametrize("max_overflow", [-1, -10])
def test_db_con_ge_0(max_overflow):
    conf_dict = valid_conf_dict(max_overflow=max_overflow)
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert "Input should be greater than or equal to 0" in str(
        exc.value
    ) and "max_overflow" in str(exc.value)


def test_db_con_kw():
    params = DBConf(**valid_conf_dict()).kw
    for k in {"user", "passwd", "db", "host", "port"}:
        assert k not in params
    assert params["pool_size"] == 10
    assert params["max_overflow"] == 5
    assert params["pool_timeout"] == 30
    assert params["pool_recycle"] == 3600
    assert params["echo"] is False
    assert params["echo_pool"] is False
