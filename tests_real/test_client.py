import pytest

from smartutils.error.sys import (
    BreakerOpenError,
    ClientError,
)


@pytest.fixture(scope="function")
async def setup_config(tmp_path_factory):
    yield


@pytest.mark.parametrize("key", ["grpcbin-ok", "grpcbin-ssl-ok", "grpcbin-breaker"])
async def test_grpc_hello_with_manager(setup_config, key):
    from hello_pb2 import HelloRequest, HelloResponse  # type: ignore

    from smartutils.infra import ClientManager

    mgr = ClientManager()

    @mgr.use(key)
    async def biz():
        cli = mgr.curr
        req = HelloRequest(greeting="grpcb.in")
        resp = await cli.SayHello(req)
        assert resp.reply == "hello grpcb.in"

    await biz()


async def test_grpc_hello_with_fail(setup_config):
    from hello_pb2 import HelloRequest, HelloResponse  # type: ignore

    from smartutils.infra import ClientManager

    mgr = ClientManager()

    @mgr.use("grpcbin-fail")
    async def biz():
        cli = mgr.curr
        req = HelloRequest(greeting="grpcb.in")
        resp = await cli.SayHello(req)
        assert resp.reply == "hello grpcb.in"

    with pytest.raises(ClientError):
        await biz()


async def test_grpc_hello_with_break_fail(setup_config):
    from hello_pb2 import HelloRequest, HelloResponse  # type: ignore

    from smartutils.infra import ClientManager

    mgr = ClientManager()

    @mgr.use("grpcbin-breaker-fail")
    async def biz():
        cli = mgr.curr
        req = HelloRequest(greeting="grpcb.in")
        resp = await cli.SayHello(req)
        assert resp.reply == "hello grpcb.in"

    with pytest.raises(BreakerOpenError):
        await biz()


@pytest.mark.parametrize("key", ["grpcbin-ok", "grpcbin-ssl-ok", "grpcbin-breaker"])
async def test_request_grpc_hello_with_manager(setup_config, key):
    from hello_pb2 import HelloRequest, HelloResponse  # type: ignore

    from smartutils.infra import ClientManager

    mgr = ClientManager()

    @mgr.use(key)
    async def biz():
        cli = mgr.curr
        req = HelloRequest(greeting="grpcb.in")

        resp = await cli.request(
            "tests_real.grpcbin.stub.hello_pb2_grpc.HelloServiceStub",
            "SayHello",
            req,
        )
        assert resp.reply == "hello grpcb.in"

        from hello_pb2_grpc import HelloServiceStub

        resp = await cli.request(HelloServiceStub, "SayHello", req)
        assert resp.reply == "hello grpcb.in"

    await biz()


async def test_grpc_ping(setup_config):
    from smartutils.infra import ClientManager

    mgr = ClientManager()

    @mgr.use("grpcbin-ok")
    async def biz():
        cli = mgr.curr
        assert await cli.ping() is True

    await biz()


HTTPBIN = "https://httpbin.org"


@pytest.mark.parametrize("key", ["httpbin-ok", "httpbin-breaker"])
async def test_client_http_manager_ip(setup_config, key):
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.get_ip()
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert "origin" in resp.json()

    await biz()


async def test_client_http_manager_breaker_fail(setup_config):
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

    @http_mgr.use("httpbin-breaker-fail")
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.delay()
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert "origin" in resp.json()

    with pytest.raises(BreakerOpenError):
        await biz()


async def test_client_http_manager_fail(setup_config):
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

    @http_mgr.use("httpbin-fail")
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.delay()
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert "origin" in resp.json()

    with pytest.raises(ClientError):
        await biz()


async def test_client_http_manager_breaker_fail_get(setup_config):
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

    @http_mgr.use("httpbin-breaker-fail")
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.get("/delay/1000")
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert "origin" in resp.json()

    with pytest.raises(BreakerOpenError):
        await biz()


@pytest.mark.parametrize("key", ["httpbin-ok", "httpbin-breaker"])
async def test_client_http_manager_get(setup_config, key):
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.get("/ip")
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert "origin" in resp.json()

    await biz()


@pytest.mark.parametrize("key", ["httpbin-ok", "httpbin-breaker"])
async def test_client_http_manager_anything_post(setup_config, key):
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.anything_post(json={"hello": "world"})
        assert resp.status_code == 200
        assert resp.raise_for_status()
        print(resp.json())
        assert resp.json()["json"]["hello"] == "world"

    await biz()


@pytest.mark.parametrize("key", ["httpbin-ok", "httpbin-breaker"])
async def test_client_http_manager_status_500(setup_config, key):
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.status_500()
        assert resp.status_code == 500

    await biz()


@pytest.mark.parametrize("key", ["httpbin-ok", "httpbin-breaker"])
async def test_client_http_manager_request(setup_config, key):
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.request("POST", "/anything", json={"foo": "bar"})
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert resp.json()["json"]["foo"] == "bar"

    await biz()


@pytest.mark.parametrize("key", ["httpbin-ok", "httpbin-breaker"])
async def test_client_http_manager_post(setup_config, key):
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

    @http_mgr.use(key)
    async def biz():
        http_cli = http_mgr.curr
        resp = await http_cli.post("/anything", json={"foo": "bar"})
        assert resp.status_code == 200
        assert resp.raise_for_status()
        assert resp.json()["json"]["foo"] == "bar"

    await biz()


@pytest.mark.parametrize("key", ["httpbin-ok", "httpbin-breaker"])
async def test_anything_post_with_header_body_query(setup_config, key):
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

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
    from smartutils.infra import ClientManager

    http_mgr = ClientManager()

    @http_mgr.use("httpbin-ok")
    async def biz():
        http_cli = http_mgr.curr
        # httpbin 首页应为200
        ret = await http_cli.ping()
        assert ret is True

    await biz()


async def test_client_ping_fail():
    # 错误endpoint，ping应返回False
    from smartutils.config.schema.client import ClientConf
    from smartutils.infra.client.http import HttpClient

    conf = ClientConf(
        endpoint="http://not.exist.local", timeout=2, verify_tls=True, type="http"
    )
    cli = HttpClient(conf, "fail")
    ret = await cli.ping()
    assert ret is False


async def test_client_http_with_api_methods():
    from smartutils.config.schema.client import ApiConf, ClientConf

    apis = {
        "get_ip": ApiConf(path="/ip", method="GET"),
        "post_echo": ApiConf(path="/post", method="POST"),
    }
    conf = ClientConf(
        type="http",
        endpoint=HTTPBIN,
        timeout=10,
        apis=apis,
    )
    from smartutils.infra.client.http import HttpClient

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
