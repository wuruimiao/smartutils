import pytest
from fastapi.testclient import TestClient

from smartutils.app import AppHook
from smartutils.app.const import HeaderKey


@pytest.fixture
async def client(tmp_path_factory):
    config_str = """
middleware:
  app:
    - log
    - exception
    - header
project:
  name: auth
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


async def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["msg"] == "success"


def test_healthy(client):
    resp = client.get("/healthy")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["msg"] == "success"


def test_trace_id_header(client):
    resp = client.get("/")

    assert HeaderKey.X_TRACE_ID in resp.headers
    trace_id = resp.headers[HeaderKey.X_TRACE_ID]
    assert trace_id

    # 指定 header，测试透传
    custom_id = "test-trace-id"
    resp2 = client.get("/", headers={HeaderKey.X_TRACE_ID: custom_id})
    assert resp2.headers.get(HeaderKey.X_TRACE_ID) == custom_id


def test_info_header_propagation(client):
    import base64

    headers = {
        "X-User-Id": "1234",
        # username传递base64格式
        "X-User-Name": base64.b64encode("tester".encode("utf-8")).decode("utf-8"),
        "X-Trace-ID": "abcde-12345",
    }
    resp = client.get("/info", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    payload = data["data"]
    assert payload["userid"] == 1234
    assert payload["username"] == "tester"
    assert payload["traceid"] == "abcde-12345"
