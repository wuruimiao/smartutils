"""
smartutils.error.base
---------------------

定义标准化的 API 错误和响应数据结构基类。

本模块旨在统一项目中的异常对象与响应体数据，便于异常与 API 返回格式互转，支持灵活扩展自定义业务异常和响应结构。
"""

from abc import ABC
from typing import Any, Dict, Optional

__all__ = ["BaseError", "BaseData", "BaseDataDict", "OK"]

_DEBUG: bool = False


class BaseDataDict(dict):
    """
    标准响应数据 Dict，对 status_code 字段和业务数据字段进行区分管理。
    """

    @property
    def status_code(self) -> int:
        """HTTP 状态码属性（默认为 200）。"""
        return self.get("status_code", 200)

    @property
    def data(self) -> Dict:
        """剥离 status_code 后的纯业务数据部分。"""
        return {k: v for k, v in self.items() if k != "status_code"}


class BaseData:
    """
    正常响应和异常均可继承此类，实现统一的数据访问接口。
    1. 正常响应使用class ResponseModel(BaseModel, BaseData, Generic[T]):，传入data字段。
    2. 异常响应使用class BaseError(BaseData, Exception, ABC):，通常不直接使用BaseError，而是先定义好具体子类异常，使用时传入detail字段。
    """

    code: int  # 业务状态码
    msg: str  # 描述信息
    status_code: int  # HTTP 状态码
    detail: str  # 可选详细错误描述
    data: Any  # 结果对象

    @property
    def as_dict(self) -> BaseDataDict:
        """将响应数据转换为标准 Dict 结构。"""
        return BaseDataDict(
            {
                "code": self.code,
                "msg": self.msg,
                "status_code": self.status_code,
                # 全局开关控制是否返回详细错误信息
                "detail": self.detail if _DEBUG else "",
                "data": self.data,
            }
        )

    @classmethod
    def set_debug(cls, on: bool):
        """设置是否启用调试模式，调试模式下会返回更详细的错误信息。"""
        global _DEBUG
        _DEBUG = on

    @property
    def is_ok(self) -> bool:
        """判断响应是否表示成功（code == 0）。"""
        return self.code == 0


class BaseError(BaseData, Exception, ABC):
    """
    标准化的业务异常基类，兼容 Exception，具备完整响应体数据结构。
    1. 替代fastapi.HTTPException，可直接raise此异常，ExceptionPlugin捕获后响应标准结构数据。
    2. 高频接口优化，使用ResponseModel.from_error()显式响应异常数据，避免异常对象构造和栈回溯开销。
    """

    code = 1000
    msg = "Internal Server Error"
    status_code = 500
    detail = ""
    data = None

    def __init__(
        self,
        detail: str = "",
        code: Optional[int] = None,
        msg: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        self.code = code if code is not None else self.code
        self.msg = msg if msg is not None else self.msg
        self.status_code = status_code if status_code is not None else self.status_code
        self.detail = detail or self.detail
        super(Exception, self).__init__(self.detail)


OK = BaseError("", 0, "success", 200)
