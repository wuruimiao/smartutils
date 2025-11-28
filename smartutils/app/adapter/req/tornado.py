import sys

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override

__all__ = ["TornadoRequestAdapter"]


@RequestAdapterFactory.register(AppKey.TORNADO)
class TornadoRequestAdapter(RequestAdapter):
    @override
    def get_header(self, key: HeaderKey) -> str:
        return self.request.headers.get(key)

    @property
    @override
    def headers(self) -> dict:
        # Tornado request.headers 是 HTTPHeaders（dict-like）
        return self.request.headers

    @override
    def set_header(self, key: HeaderKey, value: str):
        self.request.set_header(key, value)

    @property
    @override
    def query_params(self) -> dict:
        # Tornado request.arguments 是 dict，值为 list
        # 常用 get_argument/get_query_argument 取参数
        # 这里可返回单值版
        return {
            k: v[0].decode("utf-8") if v else ""
            for k, v in self.request.query_arguments.items()
        }

    @property
    @override
    def client_host(self) -> str:
        # Tornado request.remote_ip
        return self.request.remote_ip

    @property
    @override
    def method(self) -> str:
        return self.request.method

    @property
    @override
    def url(self) -> str:
        return self.request.full_url()

    @override
    def get_cookie(self, key: str) -> str:
        return self.request.cookies.get(key)
