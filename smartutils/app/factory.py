from loguru import logger

from smartutils.app.adapter.json_resp.factory import ErrorRespAdapterFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.factory import ExcErrorFactory, ExcDetailFactory

__all__ = ["ExcJsonResp"]


class ExcJsonResp:
    @classmethod
    def handle(cls, exc: BaseException, key: AppKey) -> ResponseAdapter:
        error = ExcErrorFactory.get(exc)
        resp_fn = ErrorRespAdapterFactory.get(key)
        logger.exception("ExcJsonResp handle {e}", e=ExcDetailFactory.get(exc))
        return resp_fn(error)
