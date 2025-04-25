import pytest
from pydantic import ValidationError

from smartutils.config.schema.db import DBConf


def valid_conf_dict(**kwargs):
    # 构造一个合法的配置字典，可被**kwargs覆盖
    return {
        "user": "root",
        "passwd": "123456",
        "db": "testdb",
        "pool_size": 10,
        "max_overflow": 5,
        "pool_timeout": 30,
        "pool_recycle": 3600,
        "echo": False,
        "echo_pool": False,
        "pool_pre_ping": True,
        "pool_reset_on_return": "rollback",
        **kwargs
    }


def test_db_con_valid():
    conf = DBConf(**valid_conf_dict())
    assert conf.user == "root"
    assert conf.db == "testdb"
    assert conf.pool_size == 10
    assert conf.pool_pre_ping is True
    assert conf.pool_reset_on_return == "rollback"


@pytest.mark.parametrize("field", ["user", "passwd", "db"])
@pytest.mark.parametrize("value", ["", None, "   "])
def test_db_con_empty_fields(field, value):
    conf_dict = valid_conf_dict(**{field: value})
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert f"{field}不能为空" in str(exc.value) or 'Input should be a valid string' in str(exc.value)


@pytest.mark.parametrize("pool_size", [0, -1])
def test_db_con_invalid_pool_size(pool_size):
    conf_dict = valid_conf_dict(pool_size=pool_size)
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert "pool_size 必须大于0" in str(exc.value)


@pytest.mark.parametrize("max_overflow", [-1, -10])
def test_db_con_negative_max_overflow(max_overflow):
    conf_dict = valid_conf_dict(max_overflow=max_overflow)
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert "max_overflow 不能为负数" in str(exc.value)


@pytest.mark.parametrize("pool_reset_on_return", ["commit", "", "other"])
def test_db_con_invalid_pool_reset_on_return(pool_reset_on_return):
    conf_dict = valid_conf_dict(pool_reset_on_return=pool_reset_on_return)
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert "pool_reset_on_return 只能为 'rollback'" in str(exc.value)


@pytest.mark.parametrize("pool_pre_ping", [False, 0, None])
def test_db_con_invalid_pool_pre_ping(pool_pre_ping):
    conf_dict = valid_conf_dict(pool_pre_ping=pool_pre_ping)
    with pytest.raises(ValidationError) as exc:
        DBConf(**conf_dict)
    assert "pool_pre_ping只能为 'true'" in str(exc.value) or 'Input should be a valid string' in str(
        exc.value) or 'Input should be a valid boolean' in str(exc.value)
