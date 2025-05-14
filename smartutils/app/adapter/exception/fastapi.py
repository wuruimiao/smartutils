from typing import Union

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from smartutils.error.factory import ExcFactory, ExcFormatFactory
from smartutils.error.sys_err import ValidationError


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
