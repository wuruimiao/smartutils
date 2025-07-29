import pytest
from fastapi import APIRouter, Request
from fastapi.testclient import TestClient

from smartutils.app import AppHook
from smartutils.error.sys import LibraryUsageError


@pytest.fixture
async def client(tmp_path_factory):
    config_str = """
middleware:
  routes:
    apikey:
      - log
      - exception
      - header
      - apikey
  setting:
    apikey:
      header_key: test-X-API-Key
      keys:
        - test-api-key1
        - test-api-key2

project:
  name: auth
  debug: true
  id: 0"""

    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    @AppHook.on_startup
    async def init(app):
        from smartutils.app import MiddlewareManager

        mgr = MiddlewareManager()

        @app.get("/endpoint-plugin")
        @mgr.init_endpoint("apikey")
        async def endpoint_plugin(req: Request):
            return ResponseModel(data={"name": "endpoint-plugin"})

    from smartutils.app.main.fastapi import create_app

    app = create_app(str(config_file))

    from smartutils.app.main.fastapi import ResponseModel

    with TestClient(app) as c:
        yield c

    from smartutils.init import reset_all

    await reset_all()


async def test_endpoint_api_key_success(client):
    resp = client.get("/endpoint-plugin", headers={"test-X-API-Key": "test-api-key1"})
    data = resp.json()
    assert resp.status_code == 200
    assert data["code"] == 0
    assert data["data"]["name"] == "endpoint-plugin"


async def test_endpoint_api_key_fail_no_request(client):

    from smartutils.app import MiddlewareManager
    from smartutils.app.main.fastapi import ResponseModel

    # 创建临时app实例
    app = client.app
    assert app
    # fastapi TestClient始终有app属性
    mgr = MiddlewareManager()

    # 注册一个不合规的endpoint，应触发LibraryUsageError
    with pytest.raises(LibraryUsageError):

        @app.get("/endpoint-plugin-no-req")
        @mgr.init_endpoint("apikey")
        async def endpoint_plugin_no_req():
            return ResponseModel(data={"name": "endpoint-plugin"})

        # 触发路由，仅用于cover
        client.get(
            "/endpoint-plugin-no-req", headers={"test-X-API-Key": "test-api-key1"}
        )


async def test_endpoint_api_key_fail(client):
    resp = client.get("/endpoint-plugin", headers={"test-X-API-Key": "test-api-key3"})
    data = resp.json()
    assert resp.status_code == 401
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "ApiKeyPlugin invalid key, received: test-api-key3"
