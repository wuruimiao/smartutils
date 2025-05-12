import dataclasses

from fastapi import Header

from smartutils.app.const import HeaderKey
from smartutils.design import deprecated


@deprecated("")
@dataclasses.dataclass
class UserInfo:
    userid: int
    username: str


@deprecated("Info.get_userid Info.get_username")
def get_user_info(
    x_user_id: int = Header(..., alias=HeaderKey.X_USER_ID),
    x_username: str = Header(..., alias=HeaderKey.X_USER_NAME),
) -> UserInfo:
    """
    Deprecated: Use Info.get_userid Info.get_username instead.
    """
    return UserInfo(userid=x_user_id, username=x_username)


@deprecated("Info.get_traceid")
def get_trace_id(x_trace_id: str = Header(..., alias=HeaderKey.X_TRACE_ID)) -> str:
    """
    Deprecated: Use Info.get_traceid instead.
    """
    return x_trace_id
