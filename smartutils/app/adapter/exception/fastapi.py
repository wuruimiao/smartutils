from typing import Union

from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException

from smartutils.data import max_int
from smartutils.error.factory import ExcErrorFactory, ExcDetailFactory
from smartutils.error.mapping import HTTP_STATUS_CODE_MAP
from smartutils.error.sys import ValidationError, SysError


@ExcDetailFactory.register(PydanticValidationError)
@ExcDetailFactory.register(RequestValidationError)
def _(exc: Union[PydanticValidationError, RequestValidationError]):
    for error in exc.errors():
        loc = '.'.join(str(_loc) for _loc in error['loc'])
        msg = error['msg']
        return f"{loc}: {msg}"


@ExcErrorFactory.register(PydanticValidationError)
@ExcErrorFactory.register(RequestValidationError)
def _(exc: Union[PydanticValidationError, RequestValidationError]):
    return ValidationError(detail=ExcDetailFactory.get(exc))


@ExcErrorFactory.register(HTTPException, order=max_int())
@ExcErrorFactory.register(FastAPIHTTPException, order=max_int())
def _(exc: Union[HTTPException, FastAPIHTTPException]):
    detail = ExcDetailFactory.get(exc)
    code = exc.status_code
    err_cls = HTTP_STATUS_CODE_MAP.get(code, SysError)
    return err_cls(detail=detail)
