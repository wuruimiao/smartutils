import sys

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override

__all__ = ["SanicRequestAdapter"]


@RequestAdapterFactory.register(AppKey.SANIC)
class SanicRequestAdapter(RequestAdapter):
    @override
    def get_header(self, key: HeaderKey) -> str:
        return self.request.headers.get(key)

    @override
    def set_header(self, key: HeaderKey, value: str):
        self.request.headers[key] = value

    @property
    @override
    def headers(self) -> dict:
        # Sanic request.headers 是 CIMultiDict，支持 dict 行为
        return self.request.headers

    @property
    @override
    def query_params(self) -> dict:
        # Sanic request.args 是 MultiDict，支持 dict 行为
        return self.request.args

    @property
    @override
    def client_host(self) -> str:
        # Sanic request.remote_addr 是客户端 IP
        return self.request.remote_addr

    @property
    @override
    def method(self) -> str:
        return self.request.method

    @property
    @override
    def url(self) -> str:
        # Sanic 没有完整 url 属性，可拼接
        return str(self.request.url)

    @override
    def get_cookie(self, key: str) -> str:
        return self.request.cookies.get(key)
