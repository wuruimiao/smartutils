from smartutils.app.adapter.abstract import RequestAdapter


class FlaskRequestAdapter(RequestAdapter):
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
