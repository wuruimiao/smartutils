from smartutils.ctx import CTXVarManager, CTXKey


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
