from loguru import logger

from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.design import singleton
from smartutils.error.factory import ExcDetailFactory, ExcErrorFactory

__all__ = ["ExcJsonResp"]


@singleton
class ExcJsonResp:
    def __init__(self, key: AppKey):
        self._key = key
        self._resp_fn = JsonRespFactory.get(key)

    def handle(self, exc: BaseException) -> ResponseAdapter:
        error = ExcErrorFactory.get(exc)
        logger.exception("ExcJsonResp handle {e}", e=ExcDetailFactory.get(exc))
        return self._resp_fn(error.as_dict)
