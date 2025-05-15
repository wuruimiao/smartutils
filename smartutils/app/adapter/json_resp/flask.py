from flask import jsonify  # noqa
from smartutils.app.adapter.json_resp.factory import ErrorRespAdapterFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.flask import FlaskResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.base import BaseError


@ErrorRespAdapterFactory.register(AppKey.FLASK)
def _(error: BaseError) -> ResponseAdapter:
    response = jsonify(error.dict())
    response.status_code = error.status_code
    return FlaskResponseAdapter(response)
