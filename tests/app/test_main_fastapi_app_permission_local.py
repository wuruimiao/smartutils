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
      - permission
  setting:
    permission:
      local: true

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
            return ResponseModel()

    from smartutils.app.main.fastapi import create_app

    app = create_app(str(config_file))

    from smartutils.app.main.resp import ResponseModel

    with TestClient(app) as c:
        yield c


async def test_permission_local_middleware_fail(client, mocker):
    resp = client.get("/info", cookies={"access_token": "fake"})
    data = resp.json()

    assert data["detail"] == "[PermissionPlugin] no supported local now."
    assert resp.status_code == 401
    assert data["code"] == 1019
    assert data["msg"] == "Unauthorized Error"
