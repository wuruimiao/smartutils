from time import perf_counter
from typing import Callable, Awaitable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.log import logger


class LogPlugin(AbstractMiddlewarePlugin):
    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        start = perf_counter()

        resp = await next_adapter()

        cost = (perf_counter() - start) * 1000
        logger.info(
            f"{req.client_host} - '{req.method} {req.url}' - "
            f"Query: {req.query_params} "
            f"Status: {resp.status_code} - "
            f"Cost: {cost:.3f} ms"
        )
        return resp
