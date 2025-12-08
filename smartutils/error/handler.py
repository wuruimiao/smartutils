from types import MappingProxyType
from typing import Union

from pydantic import ValidationError as PydanticValidationError

from smartutils.error.sys import (
    NotFoundError,
    RequestTooLargeError,
    SysError,
    TimeOutError,
    UnsupportedError,
    UnsupportedMediaTypeError,
    ValidationError,
)


class ErrorHandler:
    _map = MappingProxyType(
        {
            400: ValidationError,
            401: ValidationError,
            403: ValidationError,
            404: NotFoundError,
            405: UnsupportedError,
            408: TimeOutError,
            413: RequestTooLargeError,
            415: UnsupportedMediaTypeError,
            422: ValidationError,
            500: SysError,
        }
    )

    @classmethod
    def get_error_cls(cls, exc: BaseException) -> type[SysError]:
        code = getattr(exc, "status_code", 500)
        return cls._map.get(code, SysError)

    @staticmethod
    def format_validation_exc(
        exc: Union[PydanticValidationError, BaseException],
    ) -> str:
        """
        将 Pydantic 的 ValidationError 异常格式化为字符串，便于日志记录和调试。
        该函数提取异常中的错误信息，生成易读的多行字符串，每行描述一个字段的验证错误。
        """
        if not hasattr(exc, "errors"):
            return "Unknown Validate Fail!"

        errors = getattr(exc, "errors", lambda: [])()

        messages = []
        for err in errors:
            loc = err.get("loc", [])
            err_type = err.get("type", "")
            input_val = err.get("input", "")
            msg = err.get("msg", "")

            # 处理字段名，支持多层嵌套
            if isinstance(loc, (list, tuple)):
                field_path = ""
                for _loc in loc:
                    if isinstance(_loc, int):
                        field_path += f"[{_loc}]"
                    else:
                        if field_path:
                            field_path += f".{_loc}"
                        else:
                            field_path = str(_loc)
                field_path = field_path.lstrip(".")
            else:
                field_path = str(loc)

            messages.append(
                (
                    f"Field '{field_path}': Error type: {err_type}; "
                    f"Input value: {input_val}; "
                    f"Message: {msg}."
                )
            )
        if not messages:
            return "Param Validate Fail!"

        return "\n".join(messages)
