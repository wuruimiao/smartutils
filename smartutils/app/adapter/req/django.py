from smartutils.app.adapter.req.abstract import RequestAdapter

__all__ = ["DjangoRequestAdapter"]

from smartutils.app.const import HeaderKey


class DjangoRequestAdapter(RequestAdapter):
    def get_header(self, key: HeaderKey):
        pass

    def gen_trace_id(self) -> str:
        pass

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
