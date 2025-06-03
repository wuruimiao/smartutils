from typing import List, Optional

from smartutils.ctx import CTXVarManager, CTXKey

__all__ = ["ReqCTX"]


class ReqCTX:
    @classmethod
    def get_userid(cls) -> int:
        return CTXVarManager.get(CTXKey.USERID)

    @classmethod
    def get_username(cls) -> str:
        return CTXVarManager.get(CTXKey.USERNAME)

    @classmethod
    def get_traceid(cls) -> int:
        return CTXVarManager.get(CTXKey.TRACE_ID)

    @classmethod
    def get_permission_user_ids(cls) -> Optional[List[int]]:
        return CTXVarManager.get(CTXKey.PERMISSION_USER_IDS)
