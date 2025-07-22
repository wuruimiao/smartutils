from typing import Any, Callable, Coroutine, List, Type

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware

from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddleware,
    AbstractMiddlewarePlugin,
)
from smartutils.app.adapter.middleware.factory import (
    AddMiddlewareFactory,
    RouteMiddlewareFactory,
)
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import AppKey
from smartutils.log import logger

__all__ = []

key = AppKey.FASTAPI


class StarletteMiddleware(AbstractMiddleware, BaseHTTPMiddleware):
    def __init__(self, app, plugin: AbstractMiddlewarePlugin):
        super().__init__(app=app, plugin=plugin, key=AppKey.FASTAPI)
        self.name = plugin.key

    async def dispatch(self, request: Request, call_next):
        logger.debug(f"{self.name} middleware dispatching request")

        # 这里拿到的，必然是Request，如果不是，框架会自动封装成Request
        req: RequestAdapter = self.req_adapter(request)

        async def next_adapter():
            response: Response = await call_next(request)
            return self.resp_adapter(response)

        resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
        return resp.response


@AddMiddlewareFactory.register(key)
def _(app, plugins: List[AbstractMiddlewarePlugin]):
    # fastapi调用顺序和add顺序相反
    for plugin in plugins[::-1]:
        app.add_middleware(StarletteMiddleware, plugin)


@RouteMiddlewareFactory.register(key)
def _(plugins: List[AbstractMiddlewarePlugin]) -> Type[APIRoute]:
    if not plugins:
        return APIRoute

    _req_adapter = RequestAdapterFactory.get(key)
    _res_adapter = ResponseAdapterFactory.get(key)

    # TODO: 优化，这里可以考虑使用一个函数来处理, 和上面的类似，可以考虑使用一个函数来处理
    class PluginsAPIRoute(APIRoute):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def get_route_handler(
            self,
        ) -> Callable[[Request], Coroutine[Any, Any, Response]]:
            original_route_handler = super().get_route_handler()

            async def next_plugin(i, request) -> Response:
                if i >= len(plugins):
                    return await original_route_handler(request)

                plugin = plugins[i]
                req: RequestAdapter = _req_adapter(request)

                async def next_call():
                    response: Response = await next_plugin(i + 1, request)
                    return _res_adapter(response)

                resp: ResponseAdapter = await plugin.dispatch(req, next_call)
                return resp.response

            async def custom_route_handler(request: Request):
                return await next_plugin(0, request)

            return custom_route_handler

    return PluginsAPIRoute
    # return APIRouter(route_class=ThisRoute)
