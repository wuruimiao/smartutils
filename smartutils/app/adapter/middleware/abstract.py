from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncContextManager

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter


class AbstractMiddlewarePlugin(ABC):
    @abstractmethod
    @asynccontextmanager
    async def before_request(self, req: RequestAdapter) -> AsyncContextManager:
        yield

    @abstractmethod
    @asynccontextmanager
    async def after_request(
        self, req: RequestAdapter, resp: ResponseAdapter
    ) -> AsyncContextManager:
        yield
