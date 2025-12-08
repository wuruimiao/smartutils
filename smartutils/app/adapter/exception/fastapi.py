from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError as PydanticValidationError

from smartutils.data.int import max_int
from smartutils.error import BaseError, ErrorHandler
from smartutils.error.factory import ExcDetailFactory, ExcErrorFactory
from smartutils.error.sys import ValidationError

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
    return ErrorHandler.format_validation_exc(exc)


@ExcErrorFactory.register(PydanticValidationError)
@ExcErrorFactory.register(RequestValidationError)
def _(exc: BaseException) -> BaseError:
    return ValidationError(detail=ExcDetailFactory.dispatch(exc))


@ExcErrorFactory.register(HTTPException, order=max_int())
@ExcErrorFactory.register(FastAPIHTTPException, order=max_int())
def _(exc: BaseException) -> BaseError:
    detail = ExcDetailFactory.dispatch(exc)
    err_cls = ErrorHandler.get_error_cls(exc)
    return err_cls(detail=detail)
