from fastapi.routing import APIRoute

from smartutils.app.adapter.middleware.factory import RouteMiddlewareFactory
from smartutils.app.const import AppKey


async def test_starletee_route_middleware_factory_no_plugins():
    route = RouteMiddlewareFactory.get(AppKey.FASTAPI)(tuple([]))
    assert route is APIRoute
