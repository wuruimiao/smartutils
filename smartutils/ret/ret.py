from typing import Optional, Any, TypeVar, Generic

from fastapi import HTTPException
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: int = 0
    message: str = 'success'
    data: Optional[T] = None


def success_res(data: Any = None):
    return {'code': 0, 'message': 'success', 'data': data}


def fail_res(code: int, message: str):
    raise HTTPException(status_code=400, detail={'code': code, 'message': message})
