import sys

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override

__all__ = ["FlaskRequestAdapter"]


@RequestAdapterFactory.register(AppKey.FLASK)
class FlaskRequestAdapter(RequestAdapter):
    @override
    def get_header(self, key: HeaderKey) -> str:
        return self.request.headers.get(key)

    @override
    def set_header(self, key: HeaderKey, value: str):
        self.request.headers[key] = value

    @property
    @override
    def headers(self):
        return self.request.headers

    @property
    @override
    def query_params(self):
        return self.request.args

    @property
    @override
    def client_host(self):
        return self.request.remote_addr or "-"

    @property
    @override
    def method(self):
        return self.request.method

    @property
    @override
    def url(self):
        return self.request.url

    @override
    def get_cookie(self, key: str) -> str:
        return self.request.cookies.get(key)
