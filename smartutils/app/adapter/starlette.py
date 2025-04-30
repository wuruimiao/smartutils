from smartutils.app.adapter.abstract import RequestAdapter


class StarletteRequestAdapter(RequestAdapter):
    @property
    def headers(self):
        return self.request.headers

    @property
    def query_params(self):
        return self.request.query_params

    @property
    def client_host(self):
        return self.request.client.host if self.request.client else "-"

    @property
    def method(self):
        return self.request.method

    @property
    def url(self):
        return str(self.request.url)
