from loguru import logger

from smartutils.app.adapter.json_resp.factory import ExcJsonRespFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.factory import ExcFactory, ExcFormatFactory

__all__ = ["ExcJsonResp"]


class ExcJsonResp:
    @classmethod
    def handle(cls, exc: BaseException, key: AppKey) -> ResponseAdapter:
        mapped_exc = ExcFactory.get(exc)
        resp_fn = ExcJsonRespFactory.get(key)
        logger.exception("ExcJsonResp handle {e}", e=ExcFormatFactory.get(exc))
        return resp_fn(mapped_exc)
