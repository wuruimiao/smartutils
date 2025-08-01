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


def test_missing_httpx(mock_module_absent, reset):
    import smartutils.infra.client.http as mod

    mock_module_absent("httpx", mod=mod)

    with pytest.raises(LibraryUsageError) as exc:
        mod.HttpClient(conf=1, name="demo")
    assert str(exc.value) == "[HttpClient] depend on httpx, install first!"

    import smartutils.app.plugin.me as mod

    mock_module_absent("httpx", mod=mod)

    import smartutils.app.plugin.permission as mod

    mock_module_absent("httpx", mod=mod)


def test_tokenhelper_missing(mock_module_absent, reset):
    import smartutils.app.auth.token as mod

    mock_module_absent("jwt", mod=mod)

    with pytest.raises(LibraryUsageError) as exc:
        mod.TokenHelper(conf=1)
    assert str(exc.value) == "[TokenHelper] depend on jwt, install first!"


def test_redis_missing(mock_module_absent, reset):
    import smartutils.infra.cache.redis as mod

    mock_module_absent("redis", "redis.asyncio", mod=mod)

    with pytest.raises(LibraryUsageError) as e:
        mod.AsyncRedisCli(conf=1, name="failcli")
    assert str(e.value) == "[AsyncRedisCli] depend on redis, install first!"


def test_mongo_missing(mock_module_absent, reset):
    import smartutils.infra.db.mongo as mod
    import smartutils.infra.db.mongo_cli as mod2

    mock_module_absent("motor", "motor.motor_asyncio", mod=mod)
    mock_module_absent("motor", "motor.motor_asyncio", mod=mod2)

    with pytest.raises(LibraryUsageError) as e:
        mod2.AsyncMongoCli(conf=1, name="abc")
    assert str(e.value) == "[AsyncMongoCli] depend on motor, install first!"


def test_password_missing(mock_module_absent, reset):
    import smartutils.app.auth.password as mod

    mock_module_absent("bcrypt", mod=mod)

    with pytest.raises(LibraryUsageError) as e:
        mod.PasswordHelper()
    assert str(e.value) == "[PasswordHelper] depend on bcrypt, install first!"


def test_otp_missing(mock_module_absent, reset):
    import smartutils.app.auth.otp as mod

    mock_module_absent("pyotp", "qrcode", mod=mod)

    with pytest.raises(LibraryUsageError) as e:
        mod.OtpHelper()
    assert str(e.value) == "[OtpHelper] depend on pyotp, qrcode, install first!"


def test_missing_fastapi(mock_module_absent, reset):
    import smartutils.app.adapter.req.starlette as mod

    mock_module_absent("fastapi", mod=mod)

    import smartutils.app.adapter.resp.starlette as mod

    mock_module_absent("fastapi", mod=mod)

    import smartutils.app.adapter.exception.fastapi as mod

    mock_module_absent("fastapi.exceptions", mod=mod)

    import smartutils.app.adapter.middleware.starletee as mod

    mock_module_absent("fastapi", mod=mod)

    import smartutils.app.main.fastapi as mod

    mock_module_absent("fastapi", mod=mod)


def test_missing_django(mock_module_absent, reset):
    import smartutils.app.adapter.json_resp.django as mod

    mock_module_absent("django.http", mod=mod)


def test_missing_flask(mock_module_absent, reset):
    import smartutils.app.adapter.json_resp.flask as mod

    mock_module_absent("flask", mod=mod)

    import smartutils.app.adapter.middleware.flask as mod

    mock_module_absent("flask", mod=mod)


def test_missing_sqlalchemy(mock_module_absent, reset):
    import smartutils.app.history.model as mod

    mock_module_absent("sqlalchemy", mod=mod)

    import smartutils.app.history.service as mod

    mock_module_absent("sqlalchemy", mod=mod)

    import smartutils.infra.db.mysql as mod

    mock_module_absent("sqlalchemy.ext.asyncio", mod=mod)

    import smartutils.infra.db.postgresql as mod

    mock_module_absent("sqlalchemy.ext.asyncio", mod=mod)

    import smartutils.infra.db.sqlalchemy_cli as mod

    mock_module_absent("sqlalchemy.ext.asyncio", mod=mod)


def test_missing_kafka(mock_module_absent, reset):
    import smartutils.infra.mq.cli as mod

    mock_module_absent("aiokafka", mod=mod)


def test_missing_hashring(mock_module_absent, reset):
    import smartutils.data.hashring as mod

    mock_module_absent("uhashring", mod=mod)
