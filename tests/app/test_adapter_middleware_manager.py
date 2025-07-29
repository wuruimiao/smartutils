import pytest

from smartutils.app.adapter.middleware.manager import MiddlewareManager
from smartutils.app.const import AppKey, RunEnv
from smartutils.app.main.fastapi import create_app
from smartutils.config.schema.middleware import MiddlewareConf, MiddlewarePluginKey
from smartutils.error.sys import LibraryUsageError


async def test_middleware_manager_single():
    RunEnv.set_app(AppKey.FASTAPI)
    mgr1 = MiddlewareManager()
    mgr2 = MiddlewareManager()
    assert mgr1 is mgr2


async def test_middleware_manager_init_app_more_then_one():
    RunEnv.set_app(AppKey.FASTAPI)
    mgr = MiddlewareManager(
        MiddlewareConf(
            routes={MiddlewareManager.ROUTE_APP_KEY: [MiddlewarePluginKey.LOG]}
        )
    )
    app = create_app()
    with pytest.raises(LibraryUsageError) as exc:
        mgr.init_app(app)
    assert (
        str(exc.value)
        == "[MiddlewareManager] Cannot init middleware for app key AppKey.FASTAPI twice."
    )


async def test_middleware_manager_init_route_not_found():
    RunEnv.set_app(AppKey.FASTAPI)
    mgr = MiddlewareManager()
    with pytest.raises(LibraryUsageError) as exc:
        mgr.init_route("no_route")
    assert (
        str(exc.value)
        == "[MiddlewareManager] require no_route below middleware.routes in config.yaml."
    )
