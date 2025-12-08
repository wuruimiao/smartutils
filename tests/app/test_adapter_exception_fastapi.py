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


def make_pydantic_validation_error() -> (
    PydanticValidationError
):  # pyright: ignore[reportReturnType]
    try:
        Model(x="wrong_type")  # type: ignore
    except PydanticValidationError as exc:
        return exc


class ModelWithList(BaseModel):
    items: list[int]


def make_pydantic_validation_error_with_list() -> (
    PydanticValidationError
):  # pyright: ignore[reportReturnType]
    try:
        ModelWithList(items=["a", "b", "c"])  # type: ignore
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
    detail = fastapi.ExcDetailFactory.dispatch(exc)
    assert isinstance(detail, str)
    assert (
        detail
        == "Field 'x': Error type: int_parsing; Input value: wrong_type; Message: Input should be a valid integer, unable to parse string as an integer.\nField 'y': Error type: missing; Input value: {'x': 'wrong_type'}; Message: Field required."
    )

    exc = make_pydantic_validation_error_with_list()
    detail = fastapi.ExcDetailFactory.dispatch(exc)
    assert isinstance(detail, str)
    assert (
        detail
        == "Field 'items[0]': Error type: int_parsing; Input value: a; Message: Input should be a valid integer, unable to parse string as an integer.\nField 'items[1]': Error type: int_parsing; Input value: b; Message: Input should be a valid integer, unable to parse string as an integer.\nField 'items[2]': Error type: int_parsing; Input value: c; Message: Input should be a valid integer, unable to parse string as an integer."
    )


def test_exc_detail_factory_for_request_validation_error():
    exc = make_request_validation_error()
    detail = fastapi.ExcDetailFactory.dispatch(exc)
    assert isinstance(detail, str)
    assert (
        detail
        == "Field 'a': Error type: value_error.missing; Input value: ; Message: field required."
    )


def test_exc_detail_factory_pydantic_validation_error_no_errors_with_mocker(mocker):
    exc = make_pydantic_validation_error()
    # patch类的 errors 方法为属性访问时报AttributeError
    mocker.patch.object(
        type(exc),
        "errors",
        property(lambda self: (_ for _ in ()).throw(AttributeError())),
    )
    assert not hasattr(exc, "errors")  # hasattr 会因 AttributeError 返回 False
    assert fastapi.ExcDetailFactory.dispatch(exc) == "Unknown Validate Fail!"  # type: ignore


@pytest.mark.parametrize(
    "exc", [make_pydantic_validation_error(), make_request_validation_error()]
)
def test_exc_error_factory_validation_error(exc):
    err = fastapi.ExcErrorFactory.dispatch(exc)
    assert isinstance(err, SysValidationError)
    assert err.detail == fastapi.ExcDetailFactory.dispatch(exc)


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
    err = fastapi.ExcErrorFactory.dispatch(exc)
    assert isinstance(err, expected_cls)
    assert err.detail == fastapi.ExcDetailFactory.dispatch(exc)
