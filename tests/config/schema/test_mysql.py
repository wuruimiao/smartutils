import pytest
from pydantic import ValidationError

from smartutils.config.schema.mysql import MySQLConf


def valid_conf_dict(**kwargs):
    # 构造一份所有必填字段都合法的配置
    return {
        "user": "root",
        "passwd": "mypass",
        "db": "testdb",
        "host": "127.0.0.1",
        "port": 3306,
        "engine_options": {
            "port": 3306,
            "echo": True,
            "future": False,
            "connect_args": {"connect_timeout": 15}
        },
        **kwargs
    }


def test_mysql_conf_valid():
    conf = MySQLConf(**valid_conf_dict())
    assert conf.user == "root"
    assert conf.host == "127.0.0.1"
    assert conf.port == 3306
    assert conf.engine_options.echo is True
    assert conf.engine_options.connect_args.connect_timeout == 15
    # url属性
    assert conf.url == "mysql+asyncmy://root:mypass@127.0.0.1:3306/testdb"


def test_mysql_conf_default_engine_options():
    # 不传engine_options，使用默认
    base = valid_conf_dict()
    base.pop("engine_options")
    conf = MySQLConf(**base)
    assert conf.engine_options.port == 3306
    assert conf.engine_options.echo is False
    assert conf.engine_options.connect_args.connect_timeout == 10


@pytest.mark.parametrize("field,value", [
    ("host", ""),  # Host非法
    ("host", "!!!"),  # Host非法
    ("user", ""),  # user为空
    ("db", ""),  # db为空
])
def test_mysql_conf_invalid_fields(field, value):
    args = valid_conf_dict()
    args[field] = value
    with pytest.raises(ValidationError):
        MySQLConf(**args)


@pytest.mark.parametrize("port", [0, 65536, -1])
def test_mysql_conf_invalid_port(port):
    args = valid_conf_dict(port=port)
    with pytest.raises(ValidationError):
        MySQLConf(**args)


def test_mysql_conf_engine_options_override():
    # engine_options.port 覆盖
    args = valid_conf_dict(engine_options={"port": 5000})
    conf = MySQLConf(**args)
    assert conf.engine_options.port == 5000


def test_mysql_conf_connect_args_override():
    # connect_args.connect_timeout 覆盖
    args = valid_conf_dict(engine_options={
        "connect_args": {"connect_timeout": 99}
    })
    conf = MySQLConf(**args)
    assert conf.engine_options.connect_args.connect_timeout == 99


def test_mysql_conf_url_property():
    # url组合校验
    args = valid_conf_dict(user="abc", passwd="xyz", host="localhost", port=1234, db="testdb2")
    conf = MySQLConf(**args)
    assert conf.url == "mysql+asyncmy://abc:xyz@localhost:1234/testdb2"
