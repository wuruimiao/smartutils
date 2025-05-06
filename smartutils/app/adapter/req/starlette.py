from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.const import HeaderKey


class StarletteRequestAdapter(RequestAdapter):
    def get_header(self, key: HeaderKey):
        return self.request.headers.get(key)

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

    def gen_trace_id(self) -> str:
        return str(self.request.app.state.smartutils_gen())
