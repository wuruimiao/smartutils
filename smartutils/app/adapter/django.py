from smartutils.app.adapter.abstract import RequestAdapter


class DjangoRequestAdapter(RequestAdapter):
    @property
    def headers(self):
        # Django request.META, convert HTTP_ headers
        return {
            k[5:].replace("_", "-").title(): v
            for k, v in self.request.META.items()
            if k.startswith("HTTP_")
        }

    @property
    def query_params(self):
        return self.request.GET

    @property
    def client_host(self):
        return self.request.META.get("REMOTE_ADDR", "-")

    @property
    def method(self):
        return self.request.method

    @property
    def url(self):
        return self.request.build_absolute_uri()
