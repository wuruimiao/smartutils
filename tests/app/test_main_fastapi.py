import pytest
from fastapi.testclient import TestClient

from smartutils.app import AppHook
from smartutils.error.sys import SysError


@pytest.fixture
async def client():
    @AppHook.on_startup
    async def init(app):
        @app.get("/info")
        async def info():
            return ResponseModel()

        @app.get("/info/err")
        async def info_err():
            return ResponseModel.from_error(SysError())

    @AppHook.on_shutdown
    async def shutdown(app):
        a = 1

    from smartutils.app.main.fastapi import create_app

    app = create_app()

    from smartutils.app.main.fastapi import ResponseModel

    with TestClient(app) as c:
        yield c

    from smartutils.init import reset_all

    await reset_all()


async def test_main_fastapi_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["msg"] == "success"


async def test_main_fastapi_info(client):
    resp = client.get("/info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["msg"] == "success"


async def test_main_fastapi_info_err(client):
    resp = client.get("/info/err")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 1000
    assert data["msg"] == "Internal Server Error"
