from loguru import logger

from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import RunEnv
from smartutils.design import singleton
from smartutils.error.factory import ExcDetailFactory, ExcErrorFactory

__all__ = ["ExcJsonResp"]


@singleton
class ExcJsonResp:
    def __init__(self):
        self._key = RunEnv.get_app()
        self._resp_fn = JsonRespFactory.get(self._key)

    def handle(self, exc: BaseException) -> ResponseAdapter:
        error = ExcErrorFactory.get(exc)
        logger.exception("ExcJsonResp handle {e}", e=ExcDetailFactory.get(exc))
        return self._resp_fn(error.as_dict)
