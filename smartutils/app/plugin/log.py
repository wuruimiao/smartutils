from contextlib import asynccontextmanager
from time import perf_counter

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.ctx import CTXVarManager, CTXKeys
from smartutils.log import logger


@CTXVarManager.register(CTXKeys.TIMER)
class LogPlugin(AbstractMiddlewarePlugin):
    @asynccontextmanager
    async def before_request(self, req):
        with CTXVarManager.use(CTXKeys.TIMER, perf_counter()):
            yield

    @asynccontextmanager
    async def after_request(self, req: RequestAdapter, resp: ResponseAdapter):
        start = CTXVarManager.get(CTXKeys.TIMER)
        cost = perf_counter() - start
        logger.info(
            f"{req.client_host} - '{req.method} {req.url}' - "
            f"Query: {req.query_params} "
            f"Status: {resp.status_code} - "
            f"Cost: {cost:.3f} sec"
        )
        yield
