from django.http import JsonResponse  # noqa

from smartutils.app.adapter.json_resp.factory import ErrorRespAdapterFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.django import DjangoResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.base import BaseError


@ErrorRespAdapterFactory.register(AppKey.DJANGO)
def _(error: BaseError) -> ResponseAdapter:
    return DjangoResponseAdapter(
        JsonResponse(error.dict, status=error.status_code)
    )
