import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from smartutils.config.const import ConfKey
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.error.sys import LibraryError, LibraryUsageError, SysError
from smartutils.infra.source_manager.abstract import AbstractResource
from smartutils.infra.source_manager.manager import (
    CTXResourceManager,
    ResourceManagerRegistry,
)


class DummyResource(AbstractResource):
    def __init__(self, name):
        self.name = name
        self.closed = False

    def session(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        pass

    async def close(self):
        self.closed = True

    async def ping(self):
        return True


class DummyManager(CTXResourceManager[DummyResource]):
    pass


@pytest.fixture
@CTXVarManager.register("_test_ctx_")
def dummy_manager():
    resources = {
        ConfKey.GROUP_DEFAULT: DummyResource("default"),
        "custom_key": DummyResource("custom"),
    }
    # 用一个新的 context key 防止和用户上下文冲突
    return DummyManager(resources, context_var_name="_test_ctx_")


def test_registry_register_and_get_all(dummy_manager):
    # Manager 实例应已被注册
    assert dummy_manager in ResourceManagerRegistry.get_all()


@pytest.mark.asyncio
async def test_use_decorator_default(dummy_manager):
    called = {}

    @dummy_manager.use
    async def do_something():
        session = dummy_manager.curr
        called["ok"] = session.name
        return 123

    result = await do_something()
    assert result == 123
    assert called["ok"] == "default"


@pytest.mark.asyncio
async def test_use_decorator_with_key(dummy_manager):
    called = {}

    @dummy_manager.use("custom_key")
    async def work():
        session = dummy_manager.curr
        called["ok"] = session.name
        return "hello"

    r = await work()
    assert r == "hello"
    assert called["ok"] == "custom"


@pytest.mark.asyncio
async def test_use_decorator_function(dummy_manager):
    called = {}

    @dummy_manager.use
    async def work():
        session = dummy_manager.curr
        called["ok"] = session.name

    await work()
    assert called["ok"] == "default"


def test_curr_should_raise_without_use(dummy_manager):
    # 直接访问 curr 应抛出 LibraryUsageError
    with pytest.raises(LibraryUsageError):
        _ = dummy_manager.curr


def test_client_ok_and_no_resource(dummy_manager):
    # 能正常拿到默认 client
    cli = dummy_manager.client()
    assert cli.name == "default"

    # 不存在的 key 应抛出 LibraryError
    with pytest.raises(LibraryError):
        dummy_manager.client("no-such-key")


@pytest.mark.asyncio
async def test_close_should_set_closed(dummy_manager):
    # close 后所有资源应被标记 closed
    await dummy_manager.close()
    for r in dummy_manager._resources.values():
        assert r.closed


@pytest.mark.asyncio
async def test_close_should_handle_exception(dummy_manager):
    # 模拟 close 抛异常，不影响流程
    dummy_manager._resources["err"] = MagicMock(
        close=AsyncMock(side_effect=RuntimeError("fail"))
    )
    # logger.exception 应被调用
    with patch(
        "smartutils.infra.source_manager.manager.logger.exception"
    ) as logger_exc:
        await dummy_manager.close()
        assert logger_exc.call_count >= 1


@pytest.mark.asyncio
async def test_health_check_all_ok(dummy_manager):
    res = await dummy_manager.health_check()
    for k, v in res.items():
        assert v is True
