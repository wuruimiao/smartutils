from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import HeaderKey


class TornadoResponseAdapter(ResponseAdapter):
    def set_header(self, key: HeaderKey, value: str):
        self.response.set_header(key, value)

    @property
    def status_code(self) -> int:
        return self.response.get_status()
