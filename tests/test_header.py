import dataclasses

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from smartutils.app.fast.header import get_user_info, UserInfo

app = FastAPI()


@app.get("/me")
def read_me(user: UserInfo = Depends(get_user_info)):
    return dataclasses.asdict(user)


client = TestClient(app)


def test_get_user_info_success():
    headers = {
        "X-User-Id": "123",
        "X-User-Name": "alice"
    }
    response = client.get("/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"userid": 123, "username": "alice"}


def test_get_user_info_missing_username():
    headers = {
        "X-User-Id": "456"
    }
    response = client.get("/me", headers=headers)
    assert response.status_code == 422  # 缺少 X-User-Name


def test_get_user_info_missing_userid():
    headers = {
        "X-User-Name": "bob"
    }
    response = client.get("/me", headers=headers)
    assert response.status_code == 422  # 缺少 X-User-Id


def test_get_user_info_invalid_userid():
    headers = {
        "X-User-Id": "not-an-int",
        "X-User-Name": "charlie"
    }
    response = client.get("/me", headers=headers)
    assert response.status_code == 422  # 类型错误
