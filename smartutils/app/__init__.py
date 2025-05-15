from smartutils.app import adapter, plugin
from smartutils.app.req_ctx import ReqCTX
from smartutils.app.run import run
from smartutils.call import register_package
from smartutils.ctx import CTXVarManager, CTXKey

register_package(adapter)
register_package(plugin)

CTXVarManager.register(CTXKey.USERID)(None)
CTXVarManager.register(CTXKey.USERNAME)(None)
CTXVarManager.register(CTXKey.TRACE_ID)(None)

__all__ = [
    "ReqCTX",
    "run",
]
