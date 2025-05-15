from django.http import JsonResponse  # noqa

from smartutils.app.adapter.json_resp.factory import ExcJsonRespFactory
from smartutils.app.const import AppKey


@ExcJsonRespFactory.register(AppKey.DJANGO)
def _(error):
    return JsonResponse(
        {"code": error.code, "msg": error.msg, "detail": error.detail},
        status=error.status_code
    )
