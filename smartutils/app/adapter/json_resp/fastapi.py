from fastapi.responses import ORJSONResponse

from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.starlette import StarletteResponseAdapter
from smartutils.app.const import AppKey
from smartutils.app.adapter.json_resp.factory import ErrorRespAdapterFactory
from smartutils.error.base import BaseError


@ErrorRespAdapterFactory.register(AppKey.FASTAPI)
def _(error: BaseError) -> ResponseAdapter:
    return StarletteResponseAdapter(
        ORJSONResponse(status_code=error.status_code, content=error.dict())
    )
