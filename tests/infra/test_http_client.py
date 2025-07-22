import httpx
import orjson
import pytest

from smartutils.config.schema.client import ApiConf, ClientConf, ClientType
from smartutils.infra.client.http import HttpClient, mock_response


@pytest.fixture
def client_conf():
    api_conf = ApiConf(
        method="GET",
        path="/hello",
        timeout=3,
        mock={"msg": "mocked"},  # 用于mock
    )
    cfg = ClientConf(
        type=ClientType.HTTP,
        endpoint="https://httpbin.org",
        timeout=5,
        verify_tls=True,
        apis={"hello_api": api_conf},
    )
    return cfg


def fake_get(_data=None):
    async def m(path, *args, **kwargs):
        data = _data or {}
        req = httpx.Request("GET", path)
        return httpx.Response(
            status_code=200,
            request=req,
            content=orjson.dumps(data),
            headers={"Content-Type": "application/json"},
        )

    return m


@pytest.fixture
async def client(client_conf):
    client = HttpClient(conf=client_conf, name="test_client")

    yield client
    await client.close()


async def test_mock_response():
    data = {"data": 123}
    resp = await mock_response(ApiConf(method="GET", path="/hello", mock=data))
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/json"
    assert resp.json() == data


async def test_mock_api(client):
    resp = await client.hello_api()
    assert resp.status_code == 200
    assert resp.json() == {"msg": "mocked"}


async def test_ping_and_api_request(client_conf, monkeypatch):
    """测试真实 API 路径绑定与 ping 功能。"""
    # 构造不带mock的api conf
    no_mock_api_conf = ApiConf(
        method="GET",
        path="/get",
        timeout=2,
        mock=None,
    )
    conf = ClientConf(
        type=ClientType.HTTP,
        endpoint="https://httpbin.org",
        timeout=5,
        verify_tls=True,
        apis={"get_api": no_mock_api_conf},
    )
    client = HttpClient(conf=conf, name="real_test")
    monkeypatch.setattr(client._client, "get", fake_get())

    result = await client.ping()
    assert result is True

    # 测试动态绑定api (get_api)

    monkeypatch.setattr(client._client, "request", fake_get({"hello": "world"}))
    response = await client.get_api()
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {"hello": "world"}
    await client.close()
