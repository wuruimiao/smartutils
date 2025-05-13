from fastapi.responses import JSONResponse

from smartutils.app.const import AppKey
from smartutils.app.factory import JsonRespFactory


@JsonRespFactory.register(AppKey.FASTAPI)
def _(error):
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "msg": error.msg, "detail": error.detail}
    )
