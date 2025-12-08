from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError as PydanticValidationError

from smartutils.data.int import max_int
from smartutils.error.base import BaseError
from smartutils.error.factory import ExcDetailFactory, ExcErrorFactory
from smartutils.error.format import format_validation_exc
from smartutils.error.mapping import HTTP_STATUS_CODE_MAP
from smartutils.error.sys import SysError, ValidationError

try:
    from fastapi.exceptions import HTTPException as FastAPIHTTPException
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from fastapi.exceptions import HTTPException as FastAPIHTTPException
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException


@ExcDetailFactory.register(PydanticValidationError)
@ExcDetailFactory.register(RequestValidationError)
def _(exc: BaseException) -> str:
    return format_validation_exc(exc)


@ExcErrorFactory.register(PydanticValidationError)
@ExcErrorFactory.register(RequestValidationError)
def _(exc: BaseException) -> BaseError:
    return ValidationError(detail=ExcDetailFactory.dispatch(exc))


@ExcErrorFactory.register(HTTPException, order=max_int())
@ExcErrorFactory.register(FastAPIHTTPException, order=max_int())
def _(exc: BaseException) -> BaseError:
    detail = ExcDetailFactory.dispatch(exc)
    err_cls = HTTP_STATUS_CODE_MAP.get(getattr(exc, "status_code", 0), SysError)
    return err_cls(detail=detail)
