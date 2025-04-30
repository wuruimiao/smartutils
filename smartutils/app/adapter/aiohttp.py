from smartutils.app.adapter.abstract import RequestAdapter


class AIOHTTPRequestAdapter(RequestAdapter):
    @property
    def headers(self):
        return self.request.headers

    @property
    def query_params(self):
        return self.request.rel_url.query

    @property
    def client_host(self):
        peername = self.request.transport.get_extra_info("peername")
        return peername[0] if peername else "-"

    @property
    def method(self):
        return self.request.method

    @property
    def url(self):
        return str(self.request.url)
