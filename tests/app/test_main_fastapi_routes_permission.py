import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from smartutils.app import AppHook


@pytest.fixture
async def client(tmp_path_factory):
    config_str = """
middleware:
  routes:
    permission:
      - log
      - exception
      - header
      - permission

client:
  auth:
    type: http
    endpoint: https://httpbin.org
    timeout: 10
    verify_tls: true
    breaker_enabled: true
    breaker_fail_max: 1
    breaker_reset_timeout: 3
    apis:
      me:
        method: GET
        path: /me
      permission:
        method: GET
        path: /permission

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
        @app.get("/no-plugin")
        async def no_plugin():
            return ResponseModel(
                data={
                    "userid": ReqCTX.get_userid(),
                    "username": ReqCTX.get_username(),
                    "traceid": ReqCTX.get_traceid(),
                    "user_ids": ReqCTX.get_permission_user_ids(),
                }
            )

        from smartutils.app import MiddlewareManager

        mgr = MiddlewareManager()

        permission_router = APIRouter(route_class=mgr.init_route("permission"))

        @permission_router.get("/test-permission")
        async def permission():
            return ResponseModel(
                data={
                    "userid": ReqCTX.get_userid(),
                    "username": ReqCTX.get_username(),
                    "traceid": ReqCTX.get_traceid(),
                    "user_ids": ReqCTX.get_permission_user_ids(),
                }
            )

        app.include_router(permission_router)

    from smartutils.app.main.fastapi import create_app

    app = create_app(str(config_file))

    from smartutils.app import ReqCTX
    from smartutils.app.main.fastapi import ResponseModel

    with TestClient(app) as c:
        yield c


@pytest.fixture
async def fake_permission(mocker):
    # patch HttpClient._client.request
    async def fake_request(method, url, *args, **kwargs):
        if url.endswith("/permission"):

            class FakeResp:
                status_code = 200

                def json(self):
                    return {
                        "code": 0,
                        "data": {
                            "can_access": True,
                            "user_ids": [1, 2, 3],
                            "no permission": "",
                        },
                    }

                async def aread(self):
                    from json import dumps

                    return dumps(self.json()).encode("utf-8")

                async def aclose(self): ...

            return FakeResp()
        else:
            raise Exception("不对!!!")

    from smartutils.infra.client.http import AsyncClient

    mocker.patch.object(AsyncClient, "request", side_effect=fake_request)
    yield


async def test_routes_permission_no_plugin_success(client):
    resp = client.get("/no-plugin")
    data = resp.json()
    assert resp.status_code == 200
    assert data["data"]["userid"] == 0
    assert data["data"]["username"] == ""
    assert data["data"]["traceid"] == ""
    assert data["data"]["user_ids"] is None


async def test_routes_permission_middleware_success(client, fake_permission):
    resp = client.get("/test-permission", cookies={"access_token": "fake"})
    data = resp.json()
    assert resp.status_code == 200
    assert data["data"]["userid"] == 0
    assert data["data"]["username"] == ""
    assert data["data"]["traceid"] != ""
    assert data["data"]["user_ids"] == [1, 2, 3]


async def test_routes_permission_middleware_no_cookie(client, fake_permission):
    resp = client.get("/test-permission")
    data = resp.json()
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "[PermissionPlugin] request no cookies."


async def test_routes_permission_middleware_no_data(client, mocker):
    from smartutils.infra.client.http import AsyncClient

    class FakeResp:
        status_code = 200

        def json(self):
            return {"code": 0, "data": None}

        async def aread(self):
            from json import dumps

            return dumps(self.json()).encode("utf-8")

        async def aclose(self): ...

    mocker.patch.object(AsyncClient, "request", return_value=FakeResp())
    resp = client.get("/test-permission", cookies={"access_token": "fake"})
    data = resp.json()
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "[PermissionPlugin] no data."
