from smartutils.app import adapter as _adapter, plugin as _plugin
from smartutils.app.req_ctx import ReqCTX
from smartutils.app.run import run
from smartutils.call import register_package
from smartutils.ctx import CTXVarManager, CTXKey
from smartutils.app.hook import AppHook

register_package(_adapter)
register_package(_plugin)

CTXVarManager.register(CTXKey.USERID)(None)
CTXVarManager.register(CTXKey.USERNAME)(None)
CTXVarManager.register(CTXKey.TRACE_ID)(None)

__all__ = [
    "ReqCTX",
    "run",
]
