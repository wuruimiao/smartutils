from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from smartutils.app import AppHook
from smartutils.app.const import HeaderKey


@pytest.fixture
async def client(tmp_path_factory):
    config_str = """
middleware:
  enable:
    - log
    - exception
    - header
    - auth
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

    app = create_app(str(config_file))

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


# 用于测试 smartutils/app/plugin/permission.py


async def test_permission_middleware_success(client, fake_me_permission):
    resp = client.get("/info", cookies={"access_token": "fake"})
    assert resp.status_code == 200


async def test_permission_no_permission(client):
    async def fake_permission(api_conf, *args, **kwargs):
        class FakeResp:
            status_code = 200

            def json(self):
                return {
                    "code": 0,
                    "data": {
                        "can_access": False,
                        "user_ids": [],
                    },
                }

        return FakeResp()

    with patch(
        "smartutils.infra.client.http.HttpClient._api_request",
        new=AsyncMock(side_effect=fake_permission),
    ):
        resp = client.get("/info", cookies={"access_token": "fake"})

        assert resp.status_code == 401
        # 业务无权限时
        data = resp.json()
        assert data["code"] == 401 or "no permission" in data["msg"]
