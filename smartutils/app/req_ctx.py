from smartutils.ctx import CTXVarManager, CTXKeys


class ReqCTX:
    @classmethod
    def get_userid(cls) -> int:
        return CTXVarManager.get(CTXKeys.USERID)

    @classmethod
    def get_username(cls) -> str:
        return CTXVarManager.get(CTXKeys.USERNAME)

    @classmethod
    def get_traceid(cls) -> int:
        return CTXVarManager.get(CTXKeys.TRACE_ID)
