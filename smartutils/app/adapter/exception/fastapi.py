from typing import Union

from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from starlette.exceptions import HTTPException
from pydantic import ValidationError as PydanticValidationError

from smartutils.data import max_int
from smartutils.error.factory import ExcFactory, ExcFormatFactory
from smartutils.error.mapping import HTTP_STATUS_CODE_MAP
from smartutils.error.sys_err import ValidationError, SysError


@ExcFormatFactory.register(PydanticValidationError)
@ExcFormatFactory.register(RequestValidationError)
def _(exc: Union[PydanticValidationError, RequestValidationError]):
    for error in exc.errors():
        loc = '.'.join(str(_loc) for _loc in error['loc'])
        msg = error['msg']
        return f"{loc}: {msg}"


@ExcFactory.register(PydanticValidationError)
@ExcFactory.register(RequestValidationError)
def _(exc: Union[PydanticValidationError, RequestValidationError]):
    return ValidationError(detail=ExcFormatFactory.get(exc))


@ExcFactory.register(HTTPException, order=max_int())
@ExcFactory.register(FastAPIHTTPException, order=max_int())
def _(exc: Union[HTTPException, FastAPIHTTPException]):
    detail = ExcFormatFactory.get(exc)
    code = exc.status_code
    err_cls = HTTP_STATUS_CODE_MAP.get(code, SysError)
    return err_cls(detail=detail)
