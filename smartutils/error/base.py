from abc import ABC
from typing import Dict, Union

__all__ = ["BaseError"]


class BaseError(Exception, ABC):
    code: int = 1000
    msg: str = "Internal Server Error"
    status_code: int = 500
    detail: str = ""

    def __init__(self, detail: Union[str, BaseException] = None, code: int = None, msg: str = None,
                 status_code: int = None):
        self.code = code if code is not None else self.code
        self.msg = msg if msg is not None else self.msg
        self.status_code = status_code if status_code is not None else self.status_code
        if detail:
            if isinstance(detail, str):
                self.detail = detail
            elif isinstance(detail, BaseException):
                from smartutils.error.factory import ExcFormatFactory
                self.detail = ExcFormatFactory.get(detail)
        super().__init__(self.detail)

    def dict(self) -> Dict:
        return {"code": self.code, "msg": self.msg, "detail": self.detail}
