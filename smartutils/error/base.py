from abc import ABC
from typing import Dict

__all__ = ["BaseError", "OK"]

_DEBUG: bool = False


class BaseError(Exception, ABC):
    code: int = 1000
    msg: str = "Internal Server Error"
    status_code: int = 500
    detail: str = ""

    def __init__(self, detail: str = "", code: int = None, msg: str = None,
                 status_code: int = None):
        self.code = code if code is not None else self.code
        self.msg = msg if msg is not None else self.msg
        self.status_code = status_code if status_code is not None else self.status_code
        self.detail = detail or self.detail
        super().__init__(self.detail)

    def dict(self) -> Dict:
        return {"code": self.code, "msg": self.msg, "detail": self.detail if _DEBUG else ""}

    @classmethod
    def set_debug(cls, on: bool):
        global _DEBUG
        _DEBUG = on

    @property
    def is_ok(self) -> bool:
        return self.code != 0


class OK(BaseError):
    code = 0
    msg = "success"
    status_code = 200
