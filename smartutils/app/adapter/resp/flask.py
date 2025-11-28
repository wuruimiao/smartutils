import sys

from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override

__all__ = ["FlaskResponseAdapter"]


@ResponseAdapterFactory.register(AppKey.FLASK)
class FlaskResponseAdapter(ResponseAdapter):
    @override
    def set_header(self, key: HeaderKey, value: str):
        self._response.headers[key] = value

    @property
    @override
    def status_code(self) -> int:
        return self._response.status_code

    @status_code.setter
    @override
    def status_code(self, value: int):
        self._response.status_code = value
