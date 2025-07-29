from typing import Awaitable, Callable

import pytest
from fastapi.testclient import TestClient

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.hook import AppHook
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import MiddlewarePluginKey


@MiddlewarePluginFactory.register(MiddlewarePluginKey.FOR_TEST)
class CustomTestPlugin(AbstractMiddlewarePlugin):
    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        resp = await next_adapter()
        print(type(resp))
        resp.status_code = 500
        return resp


@pytest.fixture
async def client(tmp_path_factory):
    config_str = """
middleware:
  routes:
    app:
      - for_test
"""

    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    @AppHook.on_startup
    async def init(app):
        @app.get("/info")
        def info():
            return ResponseModel(status_code=200, data={"a": 1})

    from smartutils.app.main.fastapi import create_app

    app = create_app(str(config_file))

    from smartutils.app.main.fastapi import ResponseModel

    with TestClient(app) as c:
        yield c

    from smartutils.init import reset_all

    await reset_all()


async def test_custom_plugin_set_500(client):
    resp = client.get("/info")
    assert resp.status_code == 500
    data = resp.json()
    assert data["code"] == 0
    assert data["msg"] == "success"
    assert data["data"]["a"] == 1
