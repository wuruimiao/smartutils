from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import HeaderKey


class DjangoResponseAdapter(ResponseAdapter):
    def set_header(self, key: HeaderKey, value: str):
        self.response.headers[key] = value

    @property
    def status_code(self) -> int:
        return self.response.status_code
