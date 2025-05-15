from loguru import logger

from smartutils.app.adapter.json_resp.factory import ErrorJsonRespFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.factory import ExcErrorFactory, ExcDetailFactory

__all__ = ["ExcJsonResp"]


class ExcJsonResp:
    @classmethod
    def handle(cls, exc: BaseException, key: AppKey) -> ResponseAdapter:
        mapped_exc = ExcErrorFactory.get(exc)
        resp_fn = ErrorJsonRespFactory.get(key)
        logger.exception("ExcJsonResp handle {e}", e=ExcDetailFactory.get(exc))
        return resp_fn(mapped_exc)
