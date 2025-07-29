import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from smartutils.app import AppHook
from smartutils.error.sys import SysError


class Item(BaseModel):
    name: str
    price: float


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

        @app.get("/info/http/exception")
        async def info_http_exception():
            raise HTTPException(status_code=404, detail="User not found")

        @app.post("/info/validation/exception")
        async def info_validation_exception(item: Item):
            return item

    @AppHook.on_shutdown
    async def shutdown(app):
        a = 1  # noqa: F841

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


async def test_main_fastapi_info_http_exception(client):
    resp = client.get("/info/http/exception")
    assert resp.status_code == 404
    data = resp.json()
    assert data["code"] == 1001
    assert data["msg"] == "Not Found"
    assert data["detail"] == ""


async def test_main_fastapi_info_validation_exception(client):
    resp = client.post("/info/validation/exception")
    assert resp.status_code == 422
    data = resp.json()
    assert data["code"] == 1006
    assert data["msg"] == "Validation Error"
    assert data["detail"] == ""
