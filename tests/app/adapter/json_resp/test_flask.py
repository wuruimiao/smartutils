import json

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_flask_env():
    from flask import Flask

    app = Flask(__name__)
    app.app_context().push()


from smartutils.app.adapter.json_resp import flask as json_resp_flask
from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.resp.flask import FlaskResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.base import BaseDataDict


class DummyDataDict(BaseDataDict):
    def __init__(self, data, status_code=200):
        super().__init__(data)
        self["status_code"] = status_code


def test_flask_jsonresp_factory_registered():
    factory_func = JsonRespFactory.get(AppKey.FLASK)
    assert factory_func is not None
    dd = DummyDataDict({"b": 2}, status_code=202)
    resp = factory_func(dd)
    assert isinstance(resp, FlaskResponseAdapter)
    assert resp.response.status_code == 202
    assert json.loads(resp.response.data) == {"b": 2}


def test_flask_jsonresp_factory_normal():
    dd = DummyDataDict({"foo": "bar", "ok": True}, status_code=400)
    resp = json_resp_flask._(dd)
    assert isinstance(resp, FlaskResponseAdapter)
    assert resp.response.status_code == 400
    data = json.loads(resp.response.data)
    assert data == {"foo": "bar", "ok": True}


def test_flask_jsonresp_factory_empty():
    dd = DummyDataDict({}, status_code=204)
    resp = json_resp_flask._(dd)
    assert resp.response.status_code == 204
    assert json.loads(resp.response.data) == {}
