from smartutils.app.const import AppKey
from smartutils.app.factory import JsonRespFactory
from smartutils.log import logger

try:
    from django.http import JsonResponse  # noqa
except ImportError:
    logger.error(f"Django not installed.")


@JsonRespFactory.register(AppKey.DJANGO)
def _(error):
    return JsonResponse(
        {"code": error.code, "msg": error.msg, "detail": error.detail},
        status=error.status_code
    )
