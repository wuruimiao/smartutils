from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import HeaderKey, AppKey

__all__ = ["DjangoResponseAdapter"]


@ResponseAdapterFactory.register(AppKey.DJANGO)
class DjangoResponseAdapter(ResponseAdapter):
    def set_header(self, key: HeaderKey, value: str):
        self._response.headers[key] = value

    @property
    def status_code(self) -> int:
        return self._response.status_code
