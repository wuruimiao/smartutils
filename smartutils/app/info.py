from smartutils.ctx import ContextVarManager, CTXKey


class Info:
    @classmethod
    def get_userid(cls) -> int:
        return ContextVarManager.get(CTXKey.USERID)

    @classmethod
    def get_username(cls) -> str:
        return ContextVarManager.get(CTXKey.USERNAME)

    @classmethod
    def get_traceid(cls) -> int:
        return ContextVarManager.get(CTXKey.TRACE_ID)