import pytest
from fastapi import HTTPException

from smartutils.ret import Error, OK, INTERVAL_SERVER, TIMEOUT, ResponseModel, success_res, fail_res


def test_error_ok():
    err = Error(0, "OK", "成功")
    assert err.ok is True
    assert err.code_int == 0
    assert err.code == "OK"
    assert err.desc == "成功"
    assert str(err) == "code=0 message=OK:成功"
    assert err.error == "成功"
    assert err.dict() == {"code": 0, "message": "成功"}


def test_error_not_ok():
    err = Error(1, "NOT_OK", "失败")
    assert err.ok is False
    assert err.code_int == 1
    assert err.code == "NOT_OK"
    assert err.desc == "失败"
    assert str(err) == "code=1 message=NOT_OK:失败"
    assert err.error == "失败"
    assert err.dict() == {"code": 1, "message": "失败"}


def test_ok_constant():
    assert OK.ok is True
    assert OK.code_int == 0
    assert OK.code == ""
    assert OK.desc == ""
    assert OK.dict() == {"code": 0, "message": ""}


def test_internal_server_error():
    assert INTERVAL_SERVER.ok is False
    assert INTERVAL_SERVER.code_int == 500
    assert INTERVAL_SERVER.code == "Internal Server Error"
    assert INTERVAL_SERVER.desc == "服务内部错误，请联系管理员"


def test_timeout_error():
    assert TIMEOUT.ok is False
    assert TIMEOUT.code_int == 599
    assert TIMEOUT.code == "TIMEOUT"
    assert TIMEOUT.desc == "超时"


def test_response_model_defaults():
    resp = ResponseModel()
    assert resp.code == 0
    assert resp.message == 'success'
    assert resp.data is None


def test_response_model_with_data():
    resp = ResponseModel(data={"foo": "bar"})
    assert resp.code == 0
    assert resp.message == 'success'
    assert resp.data == {"foo": "bar"}


def test_success_response_none():
    result = success_res()
    assert result == {'code': 0, 'message': 'success', 'data': None}


def test_success_response_with_data():
    data = {"answer": 42}
    result = success_res(data)
    assert result == {'code': 0, 'message': 'success', 'data': data}


def test_error_response_raises_http_exception():
    code = 123
    message = "something failed"
    with pytest.raises(HTTPException) as exc_info:
        fail_res(code, message)
    exc = exc_info.value
    assert exc.status_code == 400
    assert exc.detail == {'code': code, 'message': message}
