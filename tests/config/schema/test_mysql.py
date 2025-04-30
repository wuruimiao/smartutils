import pytest
from pydantic import ValidationError

from smartutils.config.schema.mysql import MySQLConf


def valid_conf_dict(**kwargs):
    # 构造一份所有必填字段都合法的配置
    return {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "passwd": "mypass",
        "db": "testdb",
        "pool_size": 30,
        "max_overflow": 5,
        "pool_timeout": 10,
        "pool_recycle": 7200,
        "echo": False,
        "echo_pool": False,
        "connect_timeout": None,
        "execute_timeout": None,
        **kwargs,
    }


def test_mysql_conf_valid():
    conf = MySQLConf(**valid_conf_dict())
    assert conf.user == "root"
    assert conf.host == "127.0.0.1"
    assert conf.port == 3306
    assert conf.user == "root"
    assert conf.passwd == "mypass"
    assert conf.db == "testdb"
    assert conf.pool_size == 30
    assert conf.max_overflow == 5
    assert conf.pool_timeout == 10
    assert conf.pool_recycle == 7200
    assert conf.echo is False
    assert conf.echo_pool is False
    assert conf.connect_timeout is None
    assert conf.execute_timeout is None
    assert conf.url == "mysql+asyncmy://root:mypass@127.0.0.1:3306/testdb"


def test_mysql_conf_default():
    conf = MySQLConf(host="127.0.0.1", user="root", passwd="mypass", db="testdb")
    assert conf.user == "root"
    assert conf.host == "127.0.0.1"
    assert conf.port == 3306
    assert conf.user == "root"
    assert conf.passwd == "mypass"
    assert conf.db == "testdb"
    assert conf.pool_size == 10
    assert conf.max_overflow == 5
    assert conf.pool_timeout == 10
    assert conf.pool_recycle == 3600
    assert conf.echo is False
    assert conf.echo_pool is False
    assert conf.connect_timeout is None
    assert conf.execute_timeout is None
    assert conf.url == "mysql+asyncmy://root:mypass@127.0.0.1:3306/testdb"


@pytest.mark.parametrize("field", ["connect_timeout", "execute_timeout", "port"])
@pytest.mark.parametrize("value", [1, 2, 3, 10])
def test_mysql_conf_int(field, value):
    conf_dict = valid_conf_dict()
    conf_dict[field] = value
    conf = MySQLConf(**conf_dict)
    assert getattr(conf, field) == value


def test_mysql_conf_kw():
    conf = MySQLConf(**valid_conf_dict())
    params = conf.kw
    for k in {"host", "port", "user", "passwd", "db"}:
        assert k not in params
    assert params["pool_size"] == 30
    assert params["max_overflow"] == 5
    assert params["pool_timeout"] == 10
    assert params["pool_recycle"] == 7200
    assert params["echo"] is False
    assert params["echo_pool"] is False
    assert "connect_args" not in params


@pytest.mark.parametrize("field", ["connect_timeout"])
@pytest.mark.parametrize("value", [1, 2, 3, 10])
def test_mysql_conf_kw_timeout(field, value):
    conf_dict = valid_conf_dict()
    conf_dict[field] = value
    params = MySQLConf(**conf_dict).kw
    assert "connect_args" in params
    assert params["connect_args"][field] == value


@pytest.mark.parametrize("value", [1, 2, 3, 10])
def test_mysql_conf_kw_execute_timeout(value):
    conf_dict = valid_conf_dict(execute_timeout=value)
    params = MySQLConf(**conf_dict).kw
    assert "connect_args" in params
    assert (
        params["connect_args"]["init_command"]
        == f"SET SESSION MAX_EXECUTION_TIME={value * 1000}"
    )
