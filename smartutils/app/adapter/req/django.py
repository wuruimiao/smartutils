from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

__all__ = ["DjangoRequestAdapter"]


@RequestAdapterFactory.register(AppKey.DJANGO)
class DjangoRequestAdapter(RequestAdapter):
    def get_header(self, key: HeaderKey) -> str:
        return self.request.headers.get(key)

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
