from smartutils.app.const import AppKey
from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.log import logger

try:
    from flask import jsonify  # noqa
except ImportError:
    logger.error("Flask not installed.")


@JsonRespFactory.register(AppKey.FLASK)
def _(error):
    response = jsonify({"code": error.code, "msg": error.msg, "detail": error.detail})
    response.status_code = error.status_code
    return response
