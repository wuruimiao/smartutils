import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_django_settings():
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(DEBUG=True)
    django.setup()


from django.http import JsonResponse

from smartutils.app.adapter.json_resp import django as json_resp_django
from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.resp.django import DjangoResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.base import BaseDataDict


class DummyDataDict(BaseDataDict):
    def __init__(self, data, status_code=200):
        super().__init__(data)
        self["status_code"] = status_code


def test_django_jsonresp_factory_registered():
    factory_func = JsonRespFactory.get(AppKey.DJANGO)
    assert factory_func is not None
    dd = DummyDataDict({"a": 1}, status_code=201)
    resp = factory_func(dd)
    assert isinstance(resp, DjangoResponseAdapter)
    assert isinstance(resp.response, JsonResponse)
    assert resp.response.status_code == 201
    assert resp.response.content == b'{"a": 1}'


def test_django_jsonresp_factory_normal():
    dd = DummyDataDict({"x": "y", "ok": True}, status_code=404)
    resp = json_resp_django._(dd)
    assert isinstance(resp, DjangoResponseAdapter)
    assert isinstance(resp.response, JsonResponse)
    assert resp.response.status_code == 404
    assert resp.response.content == b'{"x": "y", "ok": true}'


def test_django_jsonresp_factory_empty():
    dd = DummyDataDict({}, status_code=204)
    resp = json_resp_django._(dd)
    assert resp.response.status_code == 204
    assert resp.response.content == b"{}"
