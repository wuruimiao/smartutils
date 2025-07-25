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

        @app.get("/no-plugin")
        async def no_plugin():
            return ResponseModel(data={"name": "no-plugin"})

        @app.get("/endpoint-plugin")
        @mgr.init_endpoint("apikey")
        async def endpoint_plugin(req: Request):
            return ResponseModel(data={"name": "endpoint-plugin"})

        api_key_router = APIRouter(route_class=mgr.init_route("apikey"))

        @api_key_router.get("/test-api-key")
        async def api_key():
            return ResponseModel(data={"name": "test-api-key"})

        app.include_router(api_key_router)

    from smartutils.app.main.fastapi import create_app

    app = create_app(str(config_file))

    from smartutils.app.main.fastapi import ResponseModel

    with TestClient(app) as c:
        yield c

    from smartutils.init import reset_all

    await reset_all()


@pytest.fixture
async def client_secret(tmp_path_factory):
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
      secret: test-secret12345678

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

        api_key_router = APIRouter(route_class=mgr.init_route("apikey"))

        @api_key_router.get("/test-api-key-secret")
        def api_key_secret():
            return ResponseModel(data={"name": "test-api-key-secret"})

        app.include_router(api_key_router)

    from smartutils.app.main.fastapi import create_app

    app = create_app(str(config_file))

    from smartutils.app.main.fastapi import ResponseModel

    with TestClient(app) as c:
        yield c

    from smartutils.init import reset_all

    await reset_all()


async def test_routes_api_key_no_plugin_success(client):
    resp = client.get("/no-plugin")
    data = resp.json()
    assert resp.status_code == 200
    assert data["data"]["name"] == "no-plugin"


async def test_routes_api_key_success(client):
    resp = client.get("/test-api-key", headers={"test-X-API-Key": "test-api-key1"})
    data = resp.json()
    assert resp.status_code == 200
    assert data["code"] == 0
    assert data["data"]["name"] == "test-api-key"


async def test_routes_api_key_fail(client):
    resp = client.get("/test-api-key", headers={"test-X-API-Key": "test-api-key3"})
    data = resp.json()
    assert resp.status_code == 401
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "ApiKeyPlugin invalid key, received: test-api-key3"


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


async def test_routes_api_key_success_secret(client_secret):
    resp = client_secret.get(
        "/test-api-key-secret",
        headers={
            "test-X-API-Key": "test-api-key1",
            "X-API-Signature": "5dd5d49ca194ea393f943eca7c3ce94ea6c52716b5a569f4dcd83e66ef0078fc",
            "X-API-Timestamp": "1633072800",
        },
    )
    data = resp.json()
    assert resp.status_code == 200
    assert data["data"]["name"] == "test-api-key-secret"


async def test_routes_api_key_success_no_signature(client_secret):
    resp = client_secret.get(
        "/test-api-key-secret",
        headers={
            "test-X-API-Key": "test-api-key1",
        },
    )
    data = resp.json()
    assert resp.status_code == 401
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "ApiKeyPlugin missing signature or timestamp"


async def test_routes_api_key_success_invalid_signature(client_secret):
    resp = client_secret.get(
        "/test-api-key-secret",
        headers={
            "test-X-API-Key": "test-api-key1",
            "X-API-Signature": "fake_error",
            "X-API-Timestamp": "1633072800",
        },
    )
    data = resp.json()
    assert resp.status_code == 401
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "ApiKeyPlugin invalid signature"
