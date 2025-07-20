from unittest.mock import AsyncMock, patch

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from smartutils.app import AppHook


@pytest.fixture
async def client(tmp_path_factory):
    config_str = """
middleware:
  routes:
    me:
      - log
      - exception
      - header
      - me
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
        def no_plugin():
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

        me_router = APIRouter(route_class=mgr.init_route_middleware("me"))

        @me_router.get("/test-me")
        def me():
            return ResponseModel(
                data={
                    "userid": ReqCTX.get_userid(),
                    "username": ReqCTX.get_username(),
                    "traceid": ReqCTX.get_traceid(),
                    "user_ids": ReqCTX.get_permission_user_ids(),
                }
            )

        app.include_router(me_router)

        permission_router = APIRouter(
            route_class=mgr.init_route_middleware("permission")
        )

        @permission_router.get("/test-permission")
        def permission():
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

    app = await create_app(str(config_file))

    from smartutils.app import ReqCTX
    from smartutils.app.main.fastapi import ResponseModel

    with TestClient(app) as c:
        yield c

    from smartutils.init import reset_all

    await reset_all()


@pytest.fixture
async def fake_me_permission():
    # patch HttpClient._client.request
    async def fake_request(method, url, *args, **kwargs):
        if url.endswith("/me"):

            class FakeResp:  # type: ignore
                status_code = 200

                def json(self):
                    return {"code": 0, "data": {"userid": 4321, "username": "unit"}}

                async def aread(self):
                    from json import dumps

                    return dumps(self.json()).encode("utf-8")

                async def aclose(self):
                    pass

            return FakeResp()
        elif url.endswith("/permission"):

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

                async def aclose(self):
                    pass

            return FakeResp()
        else:
            raise Exception("不对!!!")

    from smartutils.infra.client.http import AsyncClient

    with patch.object(AsyncClient, "request", new=AsyncMock(side_effect=fake_request)):
        yield


async def test_routes_no_plugin_success(client):
    resp = client.get("/no-plugin")
    data = resp.json()
    assert resp.status_code == 200
    assert data["data"]["userid"] == 0
    assert data["data"]["username"] == ""
    assert data["data"]["traceid"] == ""
    assert data["data"]["user_ids"] is None


async def test_routes_me_middleware_success(client, fake_me_permission):
    resp = client.get("/test-me", cookies={"access_token": "fake"})
    data = resp.json()
    assert resp.status_code == 200
    assert data["data"]["userid"] == 4321
    assert data["data"]["username"] == "unit"
    assert data["data"]["traceid"] != ""
    assert data["data"]["user_ids"] is None


async def test_routes_permission_middleware_success(client, fake_me_permission):
    resp = client.get("/test-permission", cookies={"access_token": "fake"})
    data = resp.json()
    assert resp.status_code == 200
    assert data["data"]["userid"] == 0
    assert data["data"]["username"] == ""
    assert data["data"]["traceid"] != ""
    assert data["data"]["user_ids"] == [1, 2, 3]
