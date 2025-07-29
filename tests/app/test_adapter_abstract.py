from typing import Awaitable, Callable, Mapping

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey, HeaderKey, RunEnv


async def test_adapter_middleware_plugin_abstract():
    # 补齐AbstractMiddlewarePlugin dispatch
    RunEnv.set_app(AppKey.FASTAPI)

    class TestPlugin(AbstractMiddlewarePlugin):
        async def dispatch(
            self,
            req: RequestAdapter,
            next_adapter: Callable[[], Awaitable[ResponseAdapter]],
        ) -> ResponseAdapter:
            return await super().dispatch(req, next_adapter)

    plugin = TestPlugin(conf=1)  # type: ignore
    await plugin.dispatch(1, 2)  # type: ignore


async def test_req_abstract():
    # 补齐RequestAdapter的抽象方法
    class MyRequest(RequestAdapter):
        def get_header(self, key: HeaderKey) -> str:
            return super().get_header(key)

        def set_header(self, key: HeaderKey, value: str):
            return super().set_header(key, value)

        @property
        def headers(self) -> Mapping[str, str]:
            return super().headers

        @property
        def query_params(self) -> dict:
            return super().query_params

        @property
        def client_host(self) -> str:
            return super().client_host

        @property
        def method(self) -> str:
            return super().method

        @property
        def url(self) -> str:
            return super().url

        @property
        def path(self) -> str:
            return super().path

        def get_cookie(self, key: str) -> str:
            return super().get_cookie(key)

    r = MyRequest(1)
    assert r.client_host is None
    assert r.get_cookie("test") is None
    assert r.get_header("test") is None  # type: ignore
    assert r.set_header("test", "test") is None  # type: ignore
    assert r.headers is None
    assert r.query_params is None
    assert r.method is None
    assert r.url is None
    assert r.path is None


async def test_resp_abstract():
    # 补齐ResponseAdapter抽象方法
    class MyResponse(ResponseAdapter):
        def set_header(self, key: HeaderKey, value: str):
            super().set_header(key, value)

        @property
        def status_code(self) -> int:
            return super().status_code

        @status_code.setter
        def status_code(self, value: int):
            ResponseAdapter.status_code.fset(self, value)  # type: ignore

    r = MyResponse(1)
    assert r.set_header("test", "test") is None  # type: ignore
    assert r.status_code is None
    r.status_code = 300
