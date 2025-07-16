import pytest

from smartutils.config.schema.client_http import HttpApiConf, HttpClientConf
from smartutils.error.sys import BreakerOpenError, HttpClientError
from smartutils.infra.client.http import HttpClient

HTTPBIN = "https://httpbin.org"


@pytest.fixture(scope="function")
async def setup_config(tmp_path_factory):
    config_str = """
client_http:
  default:
    endpoint: https://httpbin.org
    timeout: 10
    verify_tls: true
    apis:
      get_ip:
        method: GET
        path: /ip
      status_500:
        method: GET
        path: /status/500
      anything_post:
        method: POST
        path: /anything
  breaker:
    endpoint: https://httpbin.org
    timeout: 10
    verify_tls: true
    breaker_enabled: true
    breaker_fail_max: 1
    breaker_reset_timeout: 3
    apis:
      get_ip:
        method: GET
        path: /ip
      status_500:
        method: GET
        path: /status/500
      anything_post:
        method: POST
        path: /anything
  fail:
    endpoint: https://httpbin.org
    timeout: 1
    verify_tls: true
    apis:
      delay:
        method: GET
        path: /delay/100
  breaker-fail:
    endpoint: https://httpbin.org
    timeout: 1
    verify_tls: true
    breaker_enabled: true
    breaker_fail_max: 1
    breaker_reset_timeout: 3
    apis:
      delay:
        method: GET
        path: /delay/100
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


@pytest.mark.parametrize("key", ["default", "breaker"])
async def test_CLIENT_HTTP_manager_ip(setup_config, key):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.get_ip()
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert "origin" in resp.json()

    await biz()


async def test_CLIENT_HTTP_manager_breaker_fail(setup_config):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use("breaker-fail")
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.delay()
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert "origin" in resp.json()

    with pytest.raises(BreakerOpenError):
        await biz()


async def test_CLIENT_HTTP_manager_fail(setup_config):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use("fail")
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.delay()
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert "origin" in resp.json()

    with pytest.raises(HttpClientError):
        await biz()


async def test_CLIENT_HTTP_manager_breaker_fail_get(setup_config):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use("breaker-fail")
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.get("/delay/1000")
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert "origin" in resp.json()

    with pytest.raises(BreakerOpenError):
        await biz()


@pytest.mark.parametrize("key", ["default", "breaker"])
async def test_CLIENT_HTTP_manager_get(setup_config, key):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.get("/ip")
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert "origin" in resp.json()

    await biz()


@pytest.mark.parametrize("key", ["default", "breaker"])
async def test_CLIENT_HTTP_manager_anything_post(setup_config, key):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.anything_post(json={"hello": "world"})
        assert resp.status_code == 200
        assert resp.raise_for_status()
        print(resp.json())
        assert resp.json()["json"]["hello"] == "world"

    await biz()


@pytest.mark.parametrize("key", ["default", "breaker"])
async def test_CLIENT_HTTP_manager_status_500(setup_config, key):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.status_500()
        assert resp.status_code == 500

    await biz()


@pytest.mark.parametrize("key", ["default", "breaker"])
async def test_CLIENT_HTTP_manager_request(setup_config, key):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.request("POST", "/anything", json={"foo": "bar"})
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert resp.json()["json"]["foo"] == "bar"

    await biz()


@pytest.mark.parametrize("key", ["default", "breaker"])
async def test_CLIENT_HTTP_manager_post(setup_config, key):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.post("/anything", json={"foo": "bar"})
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert resp.json()["json"]["foo"] == "bar"

    await biz()


@pytest.mark.parametrize("key", ["default", "breaker"])
async def test_anything_post_with_header_body_query(setup_config, key):
    from smartutils.infra import HttpClientManager

    http_mgr = HttpClientManager()

    @http_mgr.use(key)
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
    from smartutils.config.schema.client_http import HttpClientConf
    from smartutils.infra.client.http import HttpClient

    conf = HttpClientConf(endpoint="http://not.exist.local", timeout=2, verify_tls=True)
    cli = HttpClient(conf, "fail")
    ret = await cli.ping()
    assert ret is False


async def test_CLIENT_HTTP_with_api_methods():
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

    await client.close()
