from smartutils.app import adapter as _adapter
from smartutils.app import plugin as _plugin
from smartutils.app.hook import AppHook
from smartutils.app.main.fastapi import ResponseModel
from smartutils.app.req_ctx import ReqCTX
from smartutils.app.run_main import run
from smartutils.call import register_package
from smartutils.ctx import CTXKey, CTXVarManager

register_package(_adapter)
register_package(_plugin)

CTXVarManager.register(CTXKey.USERID)(None)
CTXVarManager.register(CTXKey.USERNAME)(None)
CTXVarManager.register(CTXKey.TRACE_ID)(None)
CTXVarManager.register(CTXKey.PERMISSION_USER_IDS)(None)

__all__ = [
    "ReqCTX",
    "run",
    "AppHook",
    "ResponseModel",
]
