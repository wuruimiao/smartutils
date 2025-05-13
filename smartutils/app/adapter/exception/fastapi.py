from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from smartutils.app.factory import ExcFactory
from smartutils.error.sys_err import ValidationError


@ExcFactory.register(RequestValidationError)
def _(exc):
    return ValidationError(detail=str(exc))


@ExcFactory.register(PydanticValidationError)
def _(exc):
    return ValidationError(detail=str(exc))
