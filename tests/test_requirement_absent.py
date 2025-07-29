from functools import partial

import pytest

from smartutils.error.sys import LibraryUsageError


@pytest.fixture
def mock_module_absent(mocker):
    from smartutils.call import mock_module_absent

    return mock_module_absent(mocker)


@pytest.fixture
def reset(mocker):
    from smartutils.design.factory import BaseFactory

    base_register_func = BaseFactory.register.__func__

    mocked_register = partial(base_register_func, only_register_once=False)
    mocker.patch.object(BaseFactory, "register", classmethod(mocked_register))


def test_importerror_when_httpx_missing(mock_module_absent, reset):
    import smartutils.infra.client.http as mod

    mock_module_absent("httpx", mod=mod)

    with pytest.raises(LibraryUsageError) as exc:
        from smartutils.infra.client.http import HttpClient

        HttpClient(conf=1, name="demo")
    assert str(exc.value) == "[HttpClient] depend on httpx, install first!"


def test_tokenhelper_missing_jwt(mock_module_absent, reset):
    import smartutils.app.auth.token as mod

    mock_module_absent("jwt", mod=mod)

    with pytest.raises(LibraryUsageError) as exc:
        from smartutils.app.auth.token import TokenHelper

        TokenHelper(conf=1)
    assert str(exc.value) == "[TokenHelper] depend on jwt, install first!"


def test_redis_missing_redis(mock_module_absent, reset):
    import smartutils.infra.cache.redis as mod

    mock_module_absent("redis", "redis.asyncio", mod=mod)

    with pytest.raises(LibraryUsageError) as e:
        from smartutils.infra.cache.redis import AsyncRedisCli

        AsyncRedisCli(conf=1, name="failcli")
    assert str(e.value) == "[AsyncRedisCli] depend on redis, install first!"


def test_assert_mongo_missing_motor(mock_module_absent, reset):
    import smartutils.infra.db.mongo as mod

    mock_module_absent("motor", "motor.motor_asyncio", mod=mod)

    with pytest.raises(LibraryUsageError) as e:
        from smartutils.infra.db.mongo import AsyncMongoCli

        AsyncMongoCli(conf=1, name="abc")
    assert "depend on motor" in str(e.value)
