from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import partial
from typing import TYPE_CHECKING, Awaitable, Callable

from smartutils.config.schema.client import ApiConf, ClientConf
from smartutils.infra.client.breaker import Breaker
from smartutils.infra.source_manager.abstract import AbstractResource
from smartutils.init.mixin import LibraryCheckMixin

try:
    from httpx import AsyncClient, ConnectError, Response, TimeoutException
except ImportError:
    pass

if TYPE_CHECKING:
    from httpx import AsyncClient, ConnectError, Response, TimeoutException


def only_connection_failures(exc):
    # 仅统计超时和连接故障
    return not isinstance(exc, (TimeoutException, ConnectError))


class HttpClient(LibraryCheckMixin, AbstractResource):
    required_libs = {"httpx": AsyncClient}

    def __init__(self, conf: ClientConf, name: str):
        super().__init__(conf=conf)

        self._conf: ClientConf = conf
        self._name = name
        self._client = AsyncClient(
            base_url=conf.endpoint,
            timeout=conf.timeout,
            verify=conf.verify_tls,
        )
        self._breaker = Breaker(name, conf, only_connection_failures)

        self._make_apis()

    def __getattr__(self, name) -> Callable[..., Awaitable[Response]]:
        attr = getattr(self._client, name)
        HTTP_METHODS = {
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "options",
            "head",
            "request",
        }
        if name in HTTP_METHODS and callable(attr):

            async def _wrapped(*args, **kwargs):
                return await self._breaker.with_breaker(lambda: attr(*args, **kwargs))

            return _wrapped
        return attr

    def _make_apis(self):
        if not self._conf.apis:
            return

        for api_name, api_conf in self._conf.apis.items():
            setattr(self, api_name, partial(self._api_request, api_conf))

    async def _api_request(self, api_conf: ApiConf, *args, **kwargs) -> Response:
        async def _do_request():
            kwargs["timeout"] = (
                kwargs.pop("timeout", None) or api_conf.timeout or self._conf.timeout
            )
            resp = await self._client.request(
                api_conf.method,
                api_conf.path,
                *args,
                **kwargs,
            )
            return resp

        return await self._breaker.with_breaker(_do_request)

    async def close(self):
        await self._client.aclose()

    async def ping(self) -> bool:
        try:
            resp = await self._client.get("/")
            resp.raise_for_status()
            return True
        except Exception:
            return False

    @asynccontextmanager
    async def db(self, use_transaction: bool) -> AsyncGenerator["HttpClient", None]:
        yield self
