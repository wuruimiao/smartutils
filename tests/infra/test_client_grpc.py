import sys
from pathlib import Path

import pytest

from smartutils.error.sys import BreakerOpenError, GrpcClientError

# 确保能找到 hello_pb2, hello_pb2_grpc
sys.path.insert(0, str(Path(__file__).parent / "grpcbin" / "stub"))

from hello_pb2 import HelloRequest, HelloResponse


@pytest.fixture(scope="function")
async def setup_config(tmp_path_factory):
    """
    动态写入grpc_client配置，并由infra统一初始化
    """
    config_str = """
grpc_client:
  default:
    endpoint: grpcb.in:9000
    apis:
      SayHello:
        stub_class: tests.infra.grpcbin.stub.hello_pb2_grpc.HelloServiceStub
        method: SayHello
  sslbin:
    endpoint: grpcb.in:9001
    tls: true
    apis:
      SayHello:
        stub_class: tests.infra.grpcbin.stub.hello_pb2_grpc.HelloServiceStub
        method: SayHello
  fail:
    endpoint: grpcb.in:9000
    timeout: 0.1
    apis:
      SayHello:
        stub_class: tests.infra.grpcbin.stub.hello_pb2_grpc.HelloServiceStub
        method: SayHello
  breaker:
    endpoint: grpcb.in:9000
    breaker_enabled: true
    breaker_fail_max: 1
    breaker_reset_timeout: 3
    apis:
      SayHello:
        stub_class: tests.infra.grpcbin.stub.hello_pb2_grpc.HelloServiceStub
        method: SayHello
  breaker-fail:
    endpoint: grpcb.in:9000
    timeout: 0.1
    breaker_enabled: true
    breaker_fail_max: 1
    breaker_reset_timeout: 3
    apis:
      SayHello:
        stub_class: tests.infra.grpcbin.stub.hello_pb2_grpc.HelloServiceStub
        method: SayHello
project:
  name: testproj
  id: 2
  description: grpc test
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


@pytest.mark.parametrize("key", ["default", "sslbin", "breaker"])
async def test_grpc_hello_with_manager(setup_config, key):
    from smartutils.infra import GrpcClientManager

    mgr = GrpcClientManager()

    @mgr.use(key)
    async def biz():
        cli = mgr.curr
        req = HelloRequest(greeting="grpcb.in")
        resp = await cli.SayHello(req)
        assert resp.reply == "hello grpcb.in"

    await biz()


async def test_grpc_hello_with_fail(setup_config):
    from smartutils.infra import GrpcClientManager

    mgr = GrpcClientManager()

    @mgr.use("fail")
    async def biz():
        cli = mgr.curr
        req = HelloRequest(greeting="grpcb.in")
        resp = await cli.SayHello(req)
        assert resp.reply == "hello grpcb.in"

    with pytest.raises(GrpcClientError):
        await biz()


async def test_grpc_hello_with_break_fail(setup_config):
    from smartutils.infra import GrpcClientManager

    mgr = GrpcClientManager()

    @mgr.use("breaker-fail")
    async def biz():
        cli = mgr.curr
        req = HelloRequest(greeting="grpcb.in")
        resp = await cli.SayHello(req)
        assert resp.reply == "hello grpcb.in"

    with pytest.raises(BreakerOpenError):
        await biz()


@pytest.mark.parametrize("key", ["default", "sslbin", "breaker"])
async def test_request_grpc_hello_with_manager(setup_config, key):
    from smartutils.infra import GrpcClientManager

    mgr = GrpcClientManager()

    @mgr.use(key)
    async def biz():
        cli = mgr.curr
        req = HelloRequest(greeting="grpcb.in")

        resp = await cli.request(
            "tests.infra.grpcbin.stub.hello_pb2_grpc.HelloServiceStub", "SayHello", req
        )
        assert resp.reply == "hello grpcb.in"

        from hello_pb2_grpc import HelloServiceStub

        resp = await cli.request(HelloServiceStub, "SayHello", req)
        assert resp.reply == "hello grpcb.in"

    await biz()


async def test_grpc_ping(setup_config):
    from smartutils.infra import GrpcClientManager

    mgr = GrpcClientManager()

    @mgr.use
    async def biz():
        cli = mgr.curr
        assert await cli.ping() is True

    await biz()
