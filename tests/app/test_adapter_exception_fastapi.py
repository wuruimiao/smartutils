import pytest
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from smartutils.app.adapter.exception import fastapi
from smartutils.error.sys import SysError
from smartutils.error.sys import ValidationError as SysValidationError


class Model(BaseModel):
    x: int
    y: str


def make_pydantic_validation_error():
    try:
        Model(x="wrong_type")  # type: ignore
    except PydanticValidationError as exc:
        return exc


def make_request_validation_error():
    # FastAPI的RequestValidationError一般传的是pydantic error结构
    return RequestValidationError(
        [{"loc": "a", "msg": "field required", "type": "value_error.missing"}]
    )


def make_fastapi_http_exception():
    return FastAPIHTTPException(status_code=422, detail="Test HTTP error")


def make_starlette_http_exception():
    return StarletteHTTPException(status_code=404, detail="Not found test")


def test_exc_detail_factory_for_validation_error():
    exc = make_pydantic_validation_error()
    detail = fastapi.ExcDetailFactory.get(exc)  # type: ignore
    assert isinstance(detail, str)
    assert (
        detail
        == "x: Input should be a valid integer, unable to parse string as an integer\ny: Field required"
    )


def test_exc_detail_factory_for_request_validation_error():
    exc = make_request_validation_error()
    detail = fastapi.ExcDetailFactory.get(exc)
    assert isinstance(detail, str)
    assert detail == "a: field required"


def test_exc_detail_factory_pydantic_validation_error_no_errors_with_mocker(mocker):
    exc = make_pydantic_validation_error()
    # patch类的 errors 方法为属性访问时报AttributeError
    mocker.patch.object(
        type(exc),
        "errors",
        property(lambda self: (_ for _ in ()).throw(AttributeError())),
    )
    assert not hasattr(exc, "errors")  # hasattr 会因 AttributeError 返回 False
    assert fastapi.ExcDetailFactory.get(exc) == "Unknown Validate Fail!"  # type: ignore


@pytest.mark.parametrize(
    "exc", [make_pydantic_validation_error(), make_request_validation_error()]
)
def test_exc_error_factory_validation_error(exc):
    err = fastapi.ExcErrorFactory.get(exc)
    assert isinstance(err, SysValidationError)
    assert err.detail == fastapi.ExcDetailFactory.get(exc)


@pytest.mark.parametrize(
    "exc_cls,status_code,expected_cls",
    [
        (make_starlette_http_exception, 404, SysError),
        (
            make_fastapi_http_exception,
            422,
            SysError,
        ),  # 补充：根据你的 HTTP_STATUS_CODE_MAP 也可做映射校验
    ],
)
def test_exc_error_factory_http_exception(exc_cls, status_code, expected_cls):
    exc = exc_cls()
    err = fastapi.ExcErrorFactory.get(exc)
    assert isinstance(err, expected_cls)
    assert err.detail == fastapi.ExcDetailFactory.get(exc)
