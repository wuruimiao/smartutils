from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

from smartutils.error.base import BaseData, BaseError

T = TypeVar("T")


class ResponseModel(BaseModel, BaseData, Generic[T]):
    code: int = 0
    msg: str = "success"
    status_code: int = 200
    detail: str = ""
    data: Optional[T] = None

    @classmethod
    def from_error(cls, error: BaseError) -> "ResponseModel":
        return ResponseModel(**error.as_dict)


class PageData(BaseModel, Generic[T]):
    # 当前页实际的数据列表
    list: List[T]
    # 当前页码，保证接口自描述性和使用便利性
    page: int
    # 每页多少条
    page_size: int
    # 总数据量
    total: int
    # 总页数（可选，前端可用）
    total_pages: Optional[int] = None
