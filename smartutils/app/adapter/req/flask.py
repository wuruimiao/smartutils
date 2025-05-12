from smartutils.app.adapter.req.abstract import RequestAdapter

__all__ = ["FlaskRequestAdapter"]


class FlaskRequestAdapter(RequestAdapter):
    def gen_trace_id(self) -> str:
        pass

    @property
    def headers(self):
        return self.request.headers

    @property
    def query_params(self):
        return self.request.args

    @property
    def client_host(self):
        return self.request.remote_addr or "-"

    @property
    def method(self):
        return self.request.method

    @property
    def url(self):
        return self.request.url
