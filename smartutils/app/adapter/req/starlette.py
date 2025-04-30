from smartutils.app.adapter.req.abstract import RequestAdapter


class StarletteRequestAdapter(RequestAdapter):
    @property
    def headers(self) -> dict:
        return self.request.headers

    @property
    def query_params(self) -> dict:
        return dict(self.request.query_params)

    @property
    def client_host(self) -> str:
        return self.request.client.host if self.request.client else "-"

    @property
    def method(self):
        return self.request.method

    @property
    def url(self):
        return str(self.request.url)

    def gen_trace_id(self) -> str:
        return str(self.request.app.state.gen())

