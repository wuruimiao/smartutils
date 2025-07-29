from smartutils.ctx.const import CTXKey
from smartutils.ctx.manager import CTXVarManager


async def test_ctx_manager_use_nested():

    with CTXVarManager.use(CTXKey.TRACE_ID, 1):
        with CTXVarManager.use(CTXKey.TRACE_ID, 2):
            assert CTXVarManager.get(CTXKey.TRACE_ID) == 1


async def test_ctx_manager_use():
    with CTXVarManager.use(CTXKey.TRACE_ID, 1):
        with CTXVarManager.use(CTXKey.CLIENT, 2):
            assert CTXVarManager.get(CTXKey.TRACE_ID) == 1
            assert CTXVarManager.get(CTXKey.CLIENT) == 2


async def test_ctx_manager_use_together():
    with (
        CTXVarManager.use(CTXKey.TRACE_ID, 1),
        CTXVarManager.use(CTXKey.USERID, 2),
    ):
        assert CTXVarManager.get(CTXKey.TRACE_ID) == 1
        assert CTXVarManager.get(CTXKey.USERID) == 2
