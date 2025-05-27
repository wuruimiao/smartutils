import pytest
from pydantic import ValidationError

from smartutils.config.schema.mysql import MySQLConf


def valid_conf_dict(**kwargs):
    # 构造一份所有必填字段都合法的配置
    base = {
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
    }
    base.update(kwargs)
    return base


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
    assert conf.url == "mysql+asyncmy://root:mypass@127.0.0.1:3306/testdb"


@pytest.mark.parametrize("field", ["port"])
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


def test_mysql_conf_kw_no_connect_args():
    # 不传 connect_timeout/execute_timeout 字段
    conf_dict = valid_conf_dict()
    params = MySQLConf(**conf_dict).kw
    assert "connect_args" not in params


def test_mysql_conf_connect_timeout_invalid():
    # connect_timeout 为 0 或负数应抛异常
    for v in [0, -1, -10]:
        conf_dict = valid_conf_dict(connect_timeout=v)
        with pytest.raises(ValidationError):
            MySQLConf(**conf_dict)


def test_mysql_conf_execute_timeout_invalid():
    # execute_timeout 为 0 或负数应抛异常
    for v in [0, -1, -10]:
        conf_dict = valid_conf_dict(execute_timeout=v)
        with pytest.raises(ValidationError):
            MySQLConf(**conf_dict)


def test_mysql_conf_host_invalid():
    # host 非法
    for v in ["", "999.999.999.999", "-badhost", "ex@mple.com"]:
        conf_dict = valid_conf_dict(host=v)
        with pytest.raises(ValidationError):
            MySQLConf(**conf_dict)


def test_mysql_conf_port_invalid():
    # port 非法
    for v in [0, 65536, -1]:
        conf_dict = valid_conf_dict(port=v)
        with pytest.raises(ValidationError):
            MySQLConf(**conf_dict)


def test_mysql_conf_pool_size_invalid():
    # pool_size 必须大于0
    conf_dict = valid_conf_dict(pool_size=0)
    with pytest.raises(ValidationError):
        MySQLConf(**conf_dict)


def test_mysql_conf_max_overflow_invalid():
    # max_overflow 必须大于等于0
    conf_dict = valid_conf_dict(max_overflow=-1)
    with pytest.raises(ValidationError):
        MySQLConf(**conf_dict)


def test_mysql_conf_pool_timeout_invalid():
    # pool_timeout 必须大于0
    conf_dict = valid_conf_dict(pool_timeout=0)
    with pytest.raises(ValidationError):
        MySQLConf(**conf_dict)


def test_mysql_conf_pool_recycle_invalid():
    # pool_recycle 必须大于0
    conf_dict = valid_conf_dict(pool_recycle=0)
    with pytest.raises(ValidationError):
        MySQLConf(**conf_dict)


def test_mysql_conf_echo_type():
    # echo 必须为 bool
    conf_dict = valid_conf_dict(echo="notbool")
    with pytest.raises(ValidationError):
        MySQLConf(**conf_dict)


def test_mysql_conf_echo_pool_type():
    # echo_pool 必须为 bool
    conf_dict = valid_conf_dict(echo_pool="notbool")
    with pytest.raises(ValidationError):
        MySQLConf(**conf_dict)
