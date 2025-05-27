import pytest
from pydantic import BaseModel, ValidationError
from smartutils.config.factory import ConfFactory
from smartutils.error.sys import ConfigError

def test_conf_factory_create_single():
    class DummyConf(BaseModel):
        foo: int
    ConfFactory.register("__test__", multi=False, require=True)(DummyConf)
    conf = ConfFactory.create("__test__", {"foo": 1})
    assert isinstance(conf, DummyConf)
    assert conf.foo == 1
    # 清理注册
    del ConfFactory._registry["__test__"]

def test_conf_factory_create_missing_required():
    class DummyConf(BaseModel):
        foo: int
    ConfFactory.register("__test__", multi=False, require=True)(DummyConf)
    with pytest.raises(ConfigError):
        ConfFactory.create("__test__", None)
    del ConfFactory._registry["__test__"]

def test_conf_factory_create_missing_not_required():
    class DummyConf2(BaseModel):
        foo: int
    ConfFactory.register("__test2__", multi=False, require=False)(DummyConf2)
    result = ConfFactory.create("__test2__", None)
    assert result is None
    del ConfFactory._registry["__test2__"]

def test_conf_factory_create_multi():
    class DummyConf3(BaseModel):
        foo: int
    ConfFactory.register("__test3__", multi=True, require=True)(DummyConf3)
    conf = ConfFactory.create("__test3__", {"default": {"foo": 2}})
    assert isinstance(conf["default"], DummyConf3)
    assert conf["default"].foo == 2
    del ConfFactory._registry["__test3__"]

def test_conf_factory_create_multi_missing_group_default():
    class DummyConf4(BaseModel):
        foo: int
    ConfFactory.register("__test4__", multi=True, require=True)(DummyConf4)
    with pytest.raises(ConfigError):
        ConfFactory.create("__test4__", {"notdefault": {"foo": 3}})
    del ConfFactory._registry["__test4__"]

def test_conf_factory_create_invalid_conf():
    class DummyConf(BaseModel):
        foo: int
    ConfFactory.register("__test__", multi=False, require=True)(DummyConf)
    with pytest.raises(ConfigError):
        ConfFactory.create("__test__", {"foo": "notint"})
    del ConfFactory._registry["__test__"]