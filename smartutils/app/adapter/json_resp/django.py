from django.http import JsonResponse  # noqa

from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.django import DjangoResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.base import BaseDataDict


@JsonRespFactory.register(AppKey.DJANGO)
def _(data: BaseDataDict) -> ResponseAdapter:
    return DjangoResponseAdapter(
        JsonResponse(data.data, status=data.status_code)
    )
