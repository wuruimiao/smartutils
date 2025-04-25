import pytest
from pydantic import ValidationError

from smartutils.config.schema.redis import RedisConf


def valid_redis_conf(**kwargs):
    # 构造一份合法的 RedisConf 配置，kwargs 可用于覆盖
    return {
        "host": "127.0.0.1",
        "port": 6379,
        "db": 1,
        "passwd": "secret",
        "timeout": 10,
        **kwargs
    }


def test_redis_conf_valid():
    conf = RedisConf(**valid_redis_conf())
    assert conf.host == "127.0.0.1"
    assert conf.port == 6379
    assert conf.db == 1
    assert conf.timeout == 10
    assert conf.passwd == "secret"


def test_redis_conf_default_values():
    conf = RedisConf(host="localhost", db=0)
    assert conf.port == 6379
    assert conf.timeout == 5
    assert conf.passwd == ""


@pytest.mark.parametrize("db", [None, -1])
def test_redis_conf_invalid_db(db):
    conf_dict = valid_redis_conf(db=db)
    with pytest.raises(ValidationError) as exc:
        RedisConf(**conf_dict)
    assert "Redis db 必须>=0" in str(exc.value) or 'Input should be a valid integer' in str(exc.value)


@pytest.mark.parametrize("timeout", [0, -1])
def test_redis_conf_invalid_timeout(timeout):
    conf_dict = valid_redis_conf(timeout=timeout)
    with pytest.raises(ValidationError) as exc:
        RedisConf(**conf_dict)
    assert "timeout必须为正整数" in str(exc.value)


# HostConf 父类校验也会生效，这里可做一个集成测试
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
