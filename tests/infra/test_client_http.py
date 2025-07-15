import pytest

from smartutils.config.schema.http_client import HttpApiConf, HttpClientConf
from smartutils.error.sys import LibraryUsageError
from smartutils.infra.client.http import HttpClient

HTTPBIN = "https://httpbin.org"


@pytest.fixture(scope="function")
async def setup_config(tmp_path_factory):
    config_str = """
http_client:
  default:
    endpoint: https://httpbin.org
    timeout: 10
    verify_ssl: true
    apis:
      get_ip:
        method: GET
        path: /ip
      post_echo:
        method: POST
        path: /post
      status_500:
        method: GET
        path: /status/500
      anything_post:
        method: POST
        path: /anything
project:
  name: testproj
  id: 1
  description: http test
  version: 1.0.0
  key: test_key
"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)
    from smartutils.init import init

    await init(str(config_file))
    yield


async def test_http_client_manager_and_api(setup_config):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use()
    async def biz():
        http_cli = http_mgr.curr
        # 配置文件
        resp = await http_cli.get_ip()
        assert resp.status_code == 200

        # 通过 request 自行指定
        echo = await http_cli.request("POST", "/post", json={"foo": "bar"})
        assert echo.status_code == 200
        assert echo.json()["json"]["foo"] == "bar"

        # 动态属性api
        resp2 = await getattr(http_cli, "get_ip")()
        assert resp2.status_code == 200

        # 未定义API访问抛错
        with pytest.raises(LibraryUsageError):
            getattr(http_cli, "notexist")

    await biz()


async def test_anything_post_with_header_body_query(setup_config):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use
    async def biz():
        cli = http_mgr.curr
        # 构造请求参数
        custom_headers = {"X-Test-Header": "test-header-value"}
        body = {"foo": "bar", "num": 123}
        qs = {"q": "value"}
        resp = await cli.anything_post(headers=custom_headers, json=body, params=qs)
        assert resp.status_code == 200
        ret = resp.json()
        # 检查原样回显
        assert ret["json"] == body
        assert ret["headers"]["X-Test-Header"] == "test-header-value"
        assert ret["args"]["q"] == "value"

    await biz()


async def test_http_client_manager_status_500(setup_config):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use()
    async def biz():
        http_cli = http_mgr.curr
        # 配置文件
        resp = await http_cli.status_500()
        assert resp.status_code == 500

    await biz()


async def test_ping_success(setup_config):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use()
    async def biz():
        http_cli = http_mgr.curr
        # httpbin 首页应为200
        ret = await http_cli.ping()
        assert ret is True


async def test_ping_fail():
    # 错误endpoint，ping应返回False
    from smartutils.config.schema.http_client import HttpClientConf
    from smartutils.infra.client.http import HttpClient

    conf = HttpClientConf(endpoint="http://not.exist.local", timeout=2, verify_ssl=True)
    cli = HttpClient(conf, "fail")
    ret = await cli.ping()
    assert ret is False


async def test_http_client_with_api_methods():
    apis = {
        "get_ip": HttpApiConf(path="/ip", method="GET"),
        "post_echo": HttpApiConf(path="/post", method="POST"),
    }
    conf = HttpClientConf(
        endpoint=HTTPBIN,
        timeout=10,
        apis=apis,
    )
    client = HttpClient(conf, "test_default")
    # 1. 测试 GET
    resp = await client.get_ip()
    assert resp.status_code == 200
    data = resp.json()
    assert "origin" in data

    # 2. 测试 POST
    resp = await client.post_echo(json={"hello": "world"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["json"] == {"hello": "world"}

    # 3. fallback：__getattr__
    resp2 = await getattr(client, "get_ip")()
    assert resp2.status_code == 200

    # 4. 通用request
    resp3 = await client.request("GET", "/get")
    assert resp3.status_code == 200

    # 5. 未注册api调用异常
    with pytest.raises(LibraryUsageError):
        await getattr(client, "unknown_api")()

    await client.close()
