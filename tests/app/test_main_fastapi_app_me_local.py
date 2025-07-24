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
  setting:
    me:
      local: true

token:
  access_exp_min: 1440
  refresh_exp_day: 5
  access_secret: access
  refresh_secret: refresh

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


async def test_me_local_middleware_success(client, mocker):
    from smartutils.app import TokenHelper, User

    mocker.patch.object(
        TokenHelper, "verify_access_token", return_value=User(id=1, name="test_user")
    )
    resp = client.get("/info", cookies={"access_token": "fake"})
    data = resp.json()
    assert data["detail"] == ""
    assert resp.status_code == 200
    assert data["data"]["userid"] == 1
    assert data["data"]["username"] == "test_user"


async def test_me_local_middleware_fail(client, mocker):
    from smartutils.app import TokenHelper

    mocker.patch.object(TokenHelper, "verify_access_token", return_value=None)
    resp = client.get("/info", cookies={"access_token": "fake"})
    data = resp.json()
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
    assert data["detail"] == "[MePlugin] verify token failed"
