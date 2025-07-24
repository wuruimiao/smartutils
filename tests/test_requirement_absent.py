import pytest

from smartutils.call import mock_module_absent
from smartutils.error.sys import LibraryUsageError


@pytest.fixture(autouse=True)
def reset():
    from smartutils.ctx.manager import CTXVarManager
    from smartutils.init.factory import InitByConfFactory

    CTXVarManager.reset()
    InitByConfFactory.reset()


def test_importerror_when_httpx_missing(mocker):
    mock_module_absent(mocker, "httpx", "smartutils.infra.client.http")

    with pytest.raises(LibraryUsageError) as exc:
        from smartutils.infra.client.http import HttpClient

        HttpClient(conf=1, name="demo")
    assert str(exc.value) == "HttpClient depend on httpx, install first!"


def test_tokenhelper_missing_jwt(mocker):
    mock_module_absent(mocker, "jwt", "smartutils.app.auth.token")

    with pytest.raises(LibraryUsageError) as exc:
        from smartutils.app.auth.token import TokenHelper

        TokenHelper(conf=1)
    assert str(exc.value) == "TokenHelper depend on jwt, install first!"


async def test_redis_missing_redis(mocker):
    # 模拟redis未导入场景
    mock_module_absent(mocker, "redis")
    mock_module_absent(mocker, "redis.asyncio", "smartutils.infra.cache.redis")

    with pytest.raises(LibraryUsageError) as e:
        from smartutils.infra.cache.redis import AsyncRedisCli

        AsyncRedisCli(conf=1, name="failcli")
    assert str(e.value) == "AsyncRedisCli depend on redis, install first!"


async def test_assert_mongo_missing_motor(mocker):
    mock_module_absent(mocker, "motor")
    mock_module_absent(mocker, "motor.motor_asyncio", "smartutils.infra.db.mongo")

    with pytest.raises(LibraryUsageError) as e:
        from smartutils.infra.db.mongo import AsyncMongoCli

        AsyncMongoCli(conf=1, name="abc")
    assert "depend on motor" in str(e.value)
