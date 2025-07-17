from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddleware,
    AbstractMiddlewarePlugin,
)
from smartutils.app.adapter.middleware.factory import (
    AddMiddlewareFactory,
)
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.log import logger

__all__ = []

key = AppKey.FASTAPI


class StarletteMiddleware(AbstractMiddleware, BaseHTTPMiddleware):
    _key = key

    def __init__(self, app, plugin: AbstractMiddlewarePlugin, name: str):
        BaseHTTPMiddleware.__init__(self, app)
        AbstractMiddleware.__init__(self, plugin)
        self._name = name

    async def dispatch(self, request: Request, call_next):
        logger.debug(f"{self._name} middleware dispatching request")

        # 这里拿到的，必然是Request，如果不是，框架会自动封装成Request
        req: RequestAdapter = self.req_adapter(request)

        async def next_adapter():
            response: Response = await call_next(request)
            return self.resp_adapter(response)

        resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
        return resp.response


@AddMiddlewareFactory.register(key)
def _(app, plugin: AbstractMiddlewarePlugin, name: str):
    app.add_middleware(StarletteMiddleware, plugin, name)
