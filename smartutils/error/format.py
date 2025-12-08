from typing import Union

from pydantic import ValidationError


def format_validation_exc(exc: Union[ValidationError, BaseException]) -> str:
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
