import pytest
from fastapi.testclient import TestClient

from smartutils.app import AppHook


@pytest.fixture
async def client(tmp_path_factory):
    config_str = """
middleware:
  routes:
    app:
      - exception

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
        async def info():
            raise Exception("Test exception")

    from smartutils.app.main.fastapi import create_app

    app = create_app(str(config_file))

    with TestClient(app) as c:
        yield c


async def test_routes_app_exception_fail(client):
    resp = client.get("/info")
    data = resp.json()
    assert resp.status_code == 500
    assert data["code"] == 1000
    assert data["msg"] == "Internal Server Error"
    assert data["detail"] == "Test exception"
