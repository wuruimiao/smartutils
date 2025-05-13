from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from smartutils.error.factory import ExcFactory, ExcFormatFactory
from smartutils.error.sys_err import ValidationError


@ExcFactory.register(RequestValidationError)
def _(exc):
    return ValidationError(detail=exc)


@ExcFormatFactory.register(PydanticValidationError)
@ExcFormatFactory.register(RequestValidationError)
def _(exc):
    for error in exc.errors():
        loc = '.'.join(str(_loc) for _loc in error['loc'])
        msg = error['msg']
        return f"{loc}: {msg}"


@ExcFactory.register(PydanticValidationError)
def _(exc):
    return ValidationError(exc)
