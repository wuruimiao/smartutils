from typing import Awaitable, Callable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey, RunEnv


async def test_adapter_middleware_plugin_abstract():
    # 为了补齐    @abstractmethod async def dispatch(
    RunEnv.set_app(AppKey.FASTAPI)

    class TestPlugin(AbstractMiddlewarePlugin):
        async def dispatch(
            self,
            req: RequestAdapter,
            next_adapter: Callable[[], Awaitable[ResponseAdapter]],
        ) -> ResponseAdapter:
            return await super().dispatch(req, next_adapter)

    plugin = TestPlugin(conf=1)
    await plugin.dispatch(1, 2)
