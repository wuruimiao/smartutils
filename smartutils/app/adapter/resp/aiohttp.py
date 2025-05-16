from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import HeaderKey, AppKey

__all__ = ["AiohttpResponseAdapter"]


@ResponseAdapterFactory.register(AppKey.AIOHTTP)
class AiohttpResponseAdapter(ResponseAdapter):
    def set_header(self, key: HeaderKey, value: str):
        self._response.headers[key] = value

    @property
    def status_code(self) -> int:
        return self._response.status
