import pytest
from pydantic import ValidationError

from smartutils.config.schema.redis import RedisConf


def valid_redis_conf(**kwargs):
    return {
        "host": "127.0.0.1",
        "port": 6379,
        "db": 1,
        "passwd": "secret",
        "execute_timeout": 10,
        **kwargs
    }


def test_redis_conf_valid():
    conf = RedisConf(**valid_redis_conf())
    assert conf.host == "127.0.0.1"
    assert conf.port == 6379
    assert conf.db == 1
    assert conf.password == "secret"


def test_redis_conf_override():
    conf = RedisConf(**valid_redis_conf(passwd='11111', host='192.168.1.111'))
    assert conf.password == '11111'
    assert conf.host == "192.168.1.111"


def test_redis_conf_default_values():
    conf = RedisConf(host="localhost", db=0)
    assert conf.port == 6379
    assert conf.password is None
    assert conf.socket_connect_timeout is None
    assert conf.socket_timeout is None


@pytest.mark.parametrize("db", [-2, -1])
def test_redis_conf_invalid_db(db):
    conf_dict = valid_redis_conf(db=db)
    with pytest.raises(ValidationError) as exc:
        RedisConf(**conf_dict)
    assert "Input should be greater than or equal to 0" in str(exc.value) and 'db' in str(exc.value)


@pytest.mark.parametrize("field", ["connect_timeout", "socket_timeout"])
@pytest.mark.parametrize("value", [0, -1])
def test_redis_conf_invalid_timeout(field, value):
    conf_dict = valid_redis_conf()
    conf_dict[field] = value
    with pytest.raises(ValidationError) as exc:
        RedisConf(**conf_dict)
    assert "Input should be greater than 0" in str(exc.value) and field in str(exc.value)


@pytest.mark.parametrize("value", [None, 1, 10, 100])
def test_redis_conf_connect_timeout(value):
    conf_dict = valid_redis_conf()
    conf_dict['connect_timeout'] = value
    conf = RedisConf(**conf_dict)
    assert conf.socket_connect_timeout is value


@pytest.mark.parametrize("value", [None, 1, 10, 100])
def test_redis_conf_socket_timeout(value):
    conf_dict = valid_redis_conf()
    conf_dict['socket_timeout'] = value
    conf = RedisConf(**conf_dict)
    assert conf.socket_timeout is value


def test_redis_conf_invalid_host_from_parent():
    conf_dict = valid_redis_conf(host="")
    with pytest.raises(ValidationError) as exc:
        RedisConf(**conf_dict)
    assert "host不能为空" in str(exc.value) or "host" in str(exc.value)


def test_redis_conf_invalid_port_from_parent():
    conf_dict = valid_redis_conf(port=70000)
    with pytest.raises(ValidationError) as exc:
        RedisConf(**conf_dict)
    assert "port必须在1-65535之间" in str(exc.value) or "port" in str(exc.value)


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "192.168.1.111"])
@pytest.mark.parametrize("port", [1, 100, 999])
def test_redis_conf_url(host, port):
    conf_dict = valid_redis_conf(host=host, port=port)
    conf = RedisConf(**conf_dict)
    assert conf.url == f"redis://{host}:{port}"


def test_redis_kw():
    params = RedisConf(**valid_redis_conf()).kw
    for k in {'host', 'port'}:
        assert k not in params
    assert params['db'] == 1
    assert params['max_connections'] == 10
    assert params['socket_connect_timeout'] is None
    assert params['socket_timeout'] is None
    assert params['password'] == "secret"
