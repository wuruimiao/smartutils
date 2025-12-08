import pytest
from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory, ConfMeta
from smartutils.error.sys import ConfigError


def test_conf_factory_create_single():
    class DummyConf(BaseModel):
        foo: int

    ConfFactory.register(ConfKey("__test__"), meta=ConfMeta(multi=False, require=True))(
        DummyConf
    )  # 类型强制转换
    conf = ConfFactory.create(ConfKey("__test__"), {"foo": 1})  # 类型强制转换
    assert isinstance(conf, DummyConf)
    assert conf.foo == 1
    # 清理注册

    ConfFactory.reset(ConfKey("__test__"))


def test_conf_factory_create_missing_required():
    class DummyConf(BaseModel):
        foo: int

    ConfFactory.register(ConfKey("__test__"), meta=ConfMeta(multi=False, require=True))(
        DummyConf
    )
    with pytest.raises(ConfigError):
        ConfFactory.create(ConfKey("__test__"), {})
    ConfFactory.reset(ConfKey("__test__"))


def test_conf_factory_create_missing_not_required():
    class DummyConf2(BaseModel):
        foo: int

    ConfFactory.register(
        ConfKey("__test2__"), meta=ConfMeta(multi=False, require=False)
    )(DummyConf2)
    result = ConfFactory.create(ConfKey("__test2__"), {})
    assert result is None
    ConfFactory.reset(ConfKey("__test2__"))


def test_conf_factory_create_multi():
    class DummyConf3(BaseModel):
        foo: int

    ConfFactory.register(ConfKey("__test3__"), meta=ConfMeta(multi=True, require=True))(
        DummyConf3
    )
    conf = ConfFactory.create(ConfKey("__test3__"), {"default": {"foo": 2}})
    assert conf
    assert isinstance(conf, dict)
    assert isinstance(conf["default"], DummyConf3)
    assert conf["default"].foo == 2
    ConfFactory.reset(ConfKey("__test3__"))


def test_conf_factory_create_multi_missing_group_default():
    class DummyConf4(BaseModel):
        foo: int

    ConfFactory.register(ConfKey("__test4__"), meta=ConfMeta(multi=True, require=True))(
        DummyConf4
    )
    # with pytest.raises(ConfigError):
    ConfFactory.create(ConfKey("__test4__"), {"notdefault": {"foo": 3}})
    ConfFactory.reset(ConfKey("__test4__"))


def test_conf_factory_create_invalid_conf():
    class DummyConf(BaseModel):
        foo: int

    ConfFactory.register(ConfKey("__test__"), meta=ConfMeta(multi=False, require=True))(
        DummyConf
    )
    with pytest.raises(ConfigError):
        ConfFactory.create(ConfKey("__test__"), {"foo": "notint"})
    ConfFactory.reset(ConfKey("__test__"))
