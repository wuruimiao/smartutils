from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

__all__ = ["StarletteRequestAdapter"]


@RequestAdapterFactory.register(AppKey.FASTAPI)
class StarletteRequestAdapter(RequestAdapter):
    def get_header(self, key: HeaderKey):
        return self.request.headers.get(key)

    def set_header(self, key: HeaderKey, value: str):
        self.request.headers[key] = value

    @property
    def query_params(self) -> dict:
        return dict(self.request.query_params)

    @property
    def client_host(self) -> str:
        return self.request.client.host if self.request.client else "-"

    @property
    def method(self) -> str:
        return self.request.method

    @property
    def url(self) -> str:
        return str(self.request.url)

    def get_cookie(self, key: str) -> str:
        return self.request.cookies.get(key)
