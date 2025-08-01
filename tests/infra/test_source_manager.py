import pytest

from smartutils.config.const import ConfKey
from smartutils.ctx import CTXVarManager
from smartutils.error.sys import LibraryUsageError
from smartutils.infra.resource.abstract import AbstractAsyncResource
from smartutils.infra.resource.manager.manager import (
    CTXResourceManager,
    ResourceManagerRegistry,
)


class DummyResource(AbstractAsyncResource):
    def __init__(self, name):
        self.name = name
        self.closed = False

    def db(self, use_transaction: bool = False):
        super().db(use_transaction)
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a): ...

    async def close(self):
        await super().close()
        self.closed = True

    async def ping(self):
        await super().ping()
        return True


class DummyManager(CTXResourceManager[DummyResource]): ...


@pytest.fixture
@CTXVarManager.register("_test_ctx_")  # type: ignore
def dummy_manager():
    resources = {
        ConfKey.GROUP_DEFAULT: DummyResource("default"),
        "custom_key": DummyResource("custom"),
    }
    return DummyManager(resources=resources, ctx_key="_test_ctx_")  # type: ignore


def test_registry_register_and_get_all(dummy_manager):
    assert dummy_manager in ResourceManagerRegistry.get_all()


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


async def test_use_decorator_function(dummy_manager):
    called = {}

    @dummy_manager.use
    async def work():
        session = dummy_manager.curr
        called["ok"] = session.name

    await work()
    assert called["ok"] == "default"


def test_curr_should_raise_without_use(dummy_manager):
    with pytest.raises(LibraryUsageError):
        _ = dummy_manager.curr


def test_client_ok_and_no_resource(dummy_manager):
    cli = dummy_manager.client()
    assert cli.name == "default"
    with pytest.raises(LibraryUsageError):
        dummy_manager.client("no-such-key")


async def test_close_should_set_closed(dummy_manager):
    await dummy_manager.close()
    for r in dummy_manager._resources.values():
        assert r.closed


async def test_close_should_handle_exception(mocker, dummy_manager):
    dummy_manager._resources["err"] = mocker.MagicMock(
        close=mocker.AsyncMock(side_effect=RuntimeError("fail"))
    )
    logger_exc = mocker.patch(
        "smartutils.infra.resource.manager.manager.logger.exception"
    )
    await dummy_manager.close()
    assert logger_exc.call_count >= 1


async def test_health_check_all_ok(dummy_manager):
    res = await dummy_manager.health_check()
    for k, v in res.items():
        assert v is True


async def test_use_decorator_catch_baseerror(dummy_manager):
    from smartutils.error.base import BaseError

    class DummyErr(BaseError): ...

    @dummy_manager.use
    async def err_func():
        raise DummyErr("err")

    import pytest

    with pytest.raises(DummyErr):
        await err_func()
