from flask import jsonify  # noqa
from smartutils.app.adapter.json_resp.factory import ErrorJsonRespFactory
from smartutils.app.const import AppKey


@ErrorJsonRespFactory.register(AppKey.FLASK)
def _(error):
    response = jsonify({"code": error.code, "msg": error.msg, "detail": error.detail})
    response.status_code = error.status_code
    return response
