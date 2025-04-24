import dataclasses

from fastapi import Header


@dataclasses.dataclass
class UserInfo:
    userid: int
    username: str


def get_user_info(x_user_id: int = Header(..., alias='X-User-Id'),
                  x_username: str = Header(..., alias='X-User-Name')) -> UserInfo:
    return UserInfo(userid=x_user_id, username=x_username)
