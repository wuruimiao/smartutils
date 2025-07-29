import json

import pytest
from fastapi.testclient import TestClient

from smartutils.app import AppHook


@pytest.fixture
async def client(tmp_path_factory):
    config_str = """
middleware:
  routes:
    app:
      - log
      - exception
      - header
      - me
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
  id: 0
"""

    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    @AppHook.on_startup
    async def init(app):
        @app.get("/info")
        async def info():
            return ResponseModel(
                data={
                    "userid": ReqCTX.get_userid(),
                    "username": ReqCTX.get_username(),
                    "traceid": ReqCTX.get_traceid(),
                    "user_ids": ReqCTX.get_permission_user_ids(),
                }
            )

    from smartutils.app.main.fastapi import create_app

    app = create_app(str(config_file))

    from smartutils.app import ReqCTX
    from smartutils.app.main.fastapi import ResponseModel

    with TestClient(app) as c:
        yield c


@pytest.fixture
async def fake_me_permission(mocker):
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

    mocker.patch.object(AsyncClient, "request", side_effect=fake_request)
    yield


async def test_me_middleware_success(client, fake_me_permission):
    resp = client.get("/info", cookies={"access_token": "fake"})
    data = resp.json()
    assert data["code"] == 0
    assert data["detail"] == ""
    assert resp.status_code == 200
    assert data["data"]["userid"] == 4321
    assert data["data"]["username"] == "unit"


async def test_me_middleware_no_cookie(client):
    resp = client.get("/info")
    assert resp.status_code == 401
    data = resp.json()
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "[MePlugin] request no cookies."


async def test_permission_middleware_success(client, fake_me_permission):
    resp = client.get("/info", cookies={"access_token": "fake"})
    assert resp.status_code == 200


class FakeAsyncResponse:
    def __init__(self, status=200, jsondata=None, text=None):
        self.status_code = status
        self._jsondata = jsondata
        self.text = text or ""

    def json(self):
        if isinstance(self._jsondata, Exception):
            raise self._jsondata
        return self._jsondata

    async def aread(self):
        return json.dumps(self.json()).encode()

    async def aclose(self):
        pass


@pytest.fixture
def patch_async_client(mocker):
    from smartutils.infra.client.http import AsyncClient

    sends = {}

    def set_me(resp: FakeAsyncResponse):
        sends["me"] = resp

    def set_permission(resp: FakeAsyncResponse):
        sends["permission"] = resp

    async def fake_request(method, url, *a, **k):
        if url.endswith("/me"):
            return sends["me"]
        elif url.endswith("/permission"):
            return sends["permission"]
        raise RuntimeError("not expect: " + url)

    mocker.patch.object(AsyncClient, "request", side_effect=fake_request)
    return set_me, set_permission


async def test_auth_me_non200(client, patch_async_client):
    set_me, set_permission = patch_async_client
    # me接口返回403
    set_me(FakeAsyncResponse(status=403, jsondata={}))
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    assert resp.status_code == 401
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "[MePlugin] return 403."


async def test_auth_me_no_data(client, patch_async_client):
    set_me, set_permission = patch_async_client
    # me接口返回403
    set_me(FakeAsyncResponse(status=200, jsondata={"code": 0, "data": {}}))
    resp = client.get("/info", cookies={"access_token": "f"})
    assert resp.status_code == 401
    data = resp.json()
    assert data["detail"] == "[MePlugin] no data."
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"


async def test_auth_me_not_json(client, patch_async_client):
    set_me, set_permission = patch_async_client
    set_me(FakeAsyncResponse(jsondata=ValueError(), text="not-json"))
    set_permission(
        FakeAsyncResponse(
            jsondata={
                "code": 0,
                "data": {"can_access": True, "user_ids": [1], "no permission": ""},
            }
        )
    )
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    # 应报返回非json
    assert resp.status_code == 401
    assert data["detail"] == "[MePlugin] return data not json. not-json."
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"


async def test_auth_me_fail_code(client, patch_async_client):
    set_me, set_permission = patch_async_client
    set_me(FakeAsyncResponse(jsondata={"code": 1, "msg": "failed"}))
    set_permission(
        FakeAsyncResponse(
            jsondata={
                "code": 0,
                "data": {"can_access": True, "user_ids": [1], "no permission": ""},
            }
        )
    )
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    assert resp.status_code == 401
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "[MePlugin] code not 0 {'code': 1, 'msg': 'failed'}."


async def test_permission_non200(client, patch_async_client):
    set_me, set_permission = patch_async_client
    set_me(
        FakeAsyncResponse(jsondata={"code": 0, "data": {"userid": 2, "username": "x"}})
    )
    set_permission(FakeAsyncResponse(status=500, jsondata={}))
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    # 权限服务非200
    assert resp.status_code == 401
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "[PermissionPlugin] return 500."


async def test_permission_not_json(client, patch_async_client):
    set_me, set_permission = patch_async_client
    set_me(
        FakeAsyncResponse(jsondata={"code": 0, "data": {"userid": 2, "username": "x"}})
    )
    set_permission(FakeAsyncResponse(jsondata=ValueError(), text="fail-json"))
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    assert resp.status_code == 401
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "[PermissionPlugin] return data not json. fail-json."


async def test_permission_fail_code(client, patch_async_client):
    set_me, set_permission = patch_async_client
    set_me(
        FakeAsyncResponse(jsondata={"code": 0, "data": {"userid": 2, "username": "x"}})
    )
    set_permission(FakeAsyncResponse(jsondata={"code": 99, "msg": "perm-fail"}))
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    assert resp.status_code == 401
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert (
        data["detail"]
        == "[PermissionPlugin] code not 0 {'code': 99, 'msg': 'perm-fail'}."
    )


async def test_permission_cannot_access(client, patch_async_client):
    set_me, set_permission = patch_async_client
    set_me(
        FakeAsyncResponse(jsondata={"code": 0, "data": {"userid": 2, "username": "x"}})
    )
    set_permission(
        FakeAsyncResponse(
            jsondata={
                "code": 0,
                "data": {
                    "can_access": False,
                    "user_ids": [44],
                },
            }
        )
    )
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    assert resp.status_code == 401
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "[PermissionPlugin] no permission"
