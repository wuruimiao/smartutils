from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import HeaderKey, AppKey
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory

__all__ = ["FlaskResponseAdapter"]


@ResponseAdapterFactory.register(AppKey.FLASK)
class FlaskResponseAdapter(ResponseAdapter):
    def set_header(self, key: HeaderKey, value: str):
        self._response.headers[key] = value

    @property
    def status_code(self) -> int:
        return self._response.status_code
