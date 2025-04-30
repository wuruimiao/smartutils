from smartutils.ctx import ContextVarManager, CTXKeys


class ReqCTX:
    @classmethod
    def get_userid(cls) -> int:
        return ContextVarManager.get(CTXKeys.USERID)

    @classmethod
    def get_username(cls) -> str:
        return ContextVarManager.get(CTXKeys.USERNAME)

    @classmethod
    def get_traceid(cls) -> int:
        return ContextVarManager.get(CTXKeys.TRACE_ID)