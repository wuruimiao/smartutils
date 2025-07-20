import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from smartutils.app import AppHook
from smartutils.app.const import HeaderKey


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
  id: 0"""

    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    @AppHook.on_startup
    async def init(app):
        @app.get("/info")
        def info():
            return ResponseModel(
                data={
                    "userid": ReqCTX.get_userid(),
                    "username": ReqCTX.get_username(),
                    "traceid": ReqCTX.get_traceid(),
                    "user_ids": ReqCTX.get_permission_user_ids(),
                }
            )

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

            class FakeResp:
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


async def test_auth_middleware_success(client, fake_me_permission):
    resp = client.get("/info", cookies={"access_token": "fake"})
    data = resp.json()
    assert data["detail"] == ""
    assert resp.status_code == 200
    print(data)
    assert data["data"]["userid"] == 4321
    assert data["data"]["username"] == "unit"


async def test_auth_middleware_no_cookie(client):
    resp = client.get("/info")
    assert resp.status_code == 401
    data = resp.json()
    assert data["code"] == 1019 or data["detail"].startswith(
        "AuthPlugin request no cookies"
    )


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
def patch_async_client(monkeypatch):
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

    monkeypatch.setattr(AsyncClient, "request", AsyncMock(side_effect=fake_request))
    return set_me, set_permission


async def test_auth_me_non200(client, patch_async_client):
    set_me, set_permission = patch_async_client
    # me接口返回403
    set_me(FakeAsyncResponse(status=403, jsondata={}))
    set_permission(
        FakeAsyncResponse(
            status=200,
            jsondata={
                "code": 0,
                "data": {"can_access": True, "user_ids": [1], "no permission": ""},
            },
        )
    )
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    assert (
        resp.status_code == 500
        or resp.status_code == 401
        or data["code"] == 1020
        or data["code"] == 1019
    )


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
    assert "return data not json" in data["detail"]


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
    assert resp.status_code == 401 and data["detail"] == "failed"


async def test_permission_non200(client, patch_async_client):
    set_me, set_permission = patch_async_client
    set_me(
        FakeAsyncResponse(jsondata={"code": 0, "data": {"userid": 2, "username": "x"}})
    )
    set_permission(FakeAsyncResponse(status=500, jsondata={}))
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    # 权限服务非200
    assert resp.status_code == 500 or data["code"] == 1020


async def test_permission_not_json(client, patch_async_client):
    set_me, set_permission = patch_async_client
    set_me(
        FakeAsyncResponse(jsondata={"code": 0, "data": {"userid": 2, "username": "x"}})
    )
    set_permission(FakeAsyncResponse(jsondata=ValueError(), text="fail-json"))
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    assert "return data not json" in data["detail"]


async def test_permission_fail_code(client, patch_async_client):
    set_me, set_permission = patch_async_client
    set_me(
        FakeAsyncResponse(jsondata={"code": 0, "data": {"userid": 2, "username": "x"}})
    )
    set_permission(FakeAsyncResponse(jsondata={"code": 99, "msg": "perm-fail"}))
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    assert resp.status_code == 401 and data["detail"] == "perm-fail"


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
                    "no permission": "no-access-tip",
                },
            }
        )
    )
    resp = client.get("/info", cookies={"access_token": "f"})
    data = resp.json()
    assert resp.status_code == 401 and data["detail"] == "no-access-tip"


# ... rest of code ...
