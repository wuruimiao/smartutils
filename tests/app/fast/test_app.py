import pytest
from fastapi.testclient import TestClient
from smartutils.app.const import HEADERKey

import pytest
from httpx import AsyncClient


@pytest.fixture(scope="module")
async def client(tmp_path_factory):
    config_str = """
project:
  name: auth
  id: 0"""

    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    from smartutils import init_all
    await init_all(str(config_file))

    from smartutils.app import create_app
    app = create_app()

    from smartutils.ret import ResponseModel
    from smartutils.app import Info

    @app.get("/info")
    def info():
        return ResponseModel(
            data={
                "userid": Info.get_userid(),
                "username": Info.get_username(),
                "traceid": Info.get_traceid()
            }
        )

    with TestClient(app) as c:
        yield c

    from smartutils import reset_all
    reset_all()


async def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data['code'] == 0
    assert data['message'] == 'success'


def test_healthy(client):
    resp = client.get("/healthy")
    assert resp.status_code == 200
    data = resp.json()
    assert data['code'] == 0
    assert data['message'] == 'success'


def test_trace_id_header(client):
    resp = client.get("/")

    assert HEADERKey.X_TRACE_ID in resp.headers
    trace_id = resp.headers[HEADERKey.X_TRACE_ID]
    assert trace_id

    # 指定 header，测试透传
    custom_id = "test-trace-id"
    resp2 = client.get("/", headers={HEADERKey.X_TRACE_ID: custom_id})
    assert resp2.headers.get(HEADERKey.X_TRACE_ID) == custom_id


def test_info_header_propagation(client):
    headers = {
        "X-User-Id": "1234",
        "X-User-Name": "tester",
        "X-Trace-ID": "abcde-12345"
    }
    resp = client.get("/info", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    # 你项目的ResponseModel结构，假设data在data字段下
    payload = data["data"]
    assert payload["userid"] == "1234"      # 或 int("1234")，看你的中间件是否自动转int
    assert payload["username"] == "tester"
    assert payload["traceid"] == "abcde-12345"