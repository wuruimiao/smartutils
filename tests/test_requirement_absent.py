import builtins
import importlib.util
import sys
from functools import partial

import pytest

from smartutils.error.sys import LibraryUsageError


@pytest.fixture
def mock_module_absent(mocker):
    """
    让 import 指定模块时真正触发 ImportError，而不是 sys.modules[name] = None
    """

    def _mock(*module_names, modname=None):
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name in module_names:
                raise ImportError(f"No module named '{name}'")
            return real_import(name, *args, **kwargs)

        mocker.patch("builtins.__import__", side_effect=fake_import)
        mocker.patch(
            "importlib.util.find_spec",
            side_effect=lambda name, *a, **kw: (
                None
                if name in module_names
                else importlib.util.find_spec(name, *a, **kw)
            ),
        )

        # 这里启用会导致real中断失败
        # 如果需要影响下游子模块（如from ... import ... 情况）
        # if modname:
        #     if modname in sys.modules:
        #         del sys.modules[modname]

    return _mock


# TODO: 模拟import ImportError
# 这里启用会导致直接失败
@pytest.fixture
def clear_smartutils():
    mod_names = [
        name
        for name in sys.modules
        if name == "smartutils" or name.startswith("smartutils.")
    ]
    orig = {}
    for name in mod_names:
        orig[name] = sys.modules[name]
        del sys.modules[name]
    yield
    sys.modules.update(orig)


@pytest.fixture
def reset(mocker):
    from smartutils.design.factory import BaseFactory

    base_register_func = BaseFactory.register.__func__

    mocked_register = partial(base_register_func, only_register_once=False)
    mocker.patch.object(BaseFactory, "register", classmethod(mocked_register))


def test_importerror_when_httpx_missing(mock_module_absent, reset):
    mock_module_absent("httpx", modname="smartutils.infra.client.http")

    with pytest.raises(LibraryUsageError) as exc:
        from smartutils.infra.client.http import HttpClient

        HttpClient(conf=1, name="demo")
    assert str(exc.value) == "HttpClient depend on httpx, install first!"


def test_tokenhelper_missing_jwt(mock_module_absent, reset):
    mock_module_absent("jwt", modname="smartutils.app.auth.token")

    with pytest.raises(LibraryUsageError) as exc:
        from smartutils.app.auth.token import TokenHelper

        TokenHelper(conf=1)
    assert str(exc.value) == "TokenHelper depend on jwt, install first!"


def test_redis_missing_redis(mock_module_absent, reset):
    mock_module_absent("redis", "redis.asyncio", modname="smartutils.infra.cache.redis")

    with pytest.raises(LibraryUsageError) as e:
        from smartutils.infra.cache.redis import AsyncRedisCli

        AsyncRedisCli(conf=1, name="failcli")
    assert str(e.value) == "AsyncRedisCli depend on redis, install first!"


def test_assert_mongo_missing_motor(mock_module_absent, reset):
    mock_module_absent(
        "motor", "motor.motor_asyncio", modname="smartutils.infra.db.mongo"
    )

    with pytest.raises(LibraryUsageError) as e:
        from smartutils.infra.db.mongo import AsyncMongoCli

        AsyncMongoCli(conf=1, name="abc")
    assert "depend on motor" in str(e.value)
