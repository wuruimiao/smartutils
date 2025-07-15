from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import partial
from typing import TYPE_CHECKING, Callable, Dict, Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.http_client import HttpApiConf, HttpClientConf
from smartutils.ctx.const import CTXKey
from smartutils.ctx.manager import CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import HttpClientError, LibraryUsageError
from smartutils.infra.factory import InfraFactory
from smartutils.infra.source_manager.abstract import AbstractResource
from smartutils.infra.source_manager.manager import CTXResourceManager

try:
    from httpx import AsyncClient, Response
except ImportError:
    pass

if TYPE_CHECKING:
    from httpx import AsyncClient
msg = "smartutils.infra.client.http depend on httpx, install before use"


class HttpClient(AbstractResource):
    def __init__(self, conf: HttpClientConf, name: str):
        self._conf = conf
        self._name = name
        assert AsyncClient, msg
        self._client = AsyncClient(
            base_url=conf.endpoint,
            timeout=conf.timeout,
            verify=conf.verify_ssl,
        )

        self._make_apis()

    def __getattr__(self, name):
        return getattr(self._client, name)

    def _make_apis(self):
        if not self._conf.apis:
            return

        for api_name, api_conf in self._conf.apis.items():
            setattr(self, api_name, partial(self._api_request, api_conf))

    async def _api_request(self, api_conf: HttpApiConf, *args, **kwargs) -> Response:
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


@singleton
@CTXVarManager.register(CTXKey.CLIENT_HTTP)
class HttpClientManager(CTXResourceManager[HttpClient]):
    def __init__(self, confs: Optional[Dict[ConfKey, HttpClientConf]] = None):
        if not confs:
            raise LibraryUsageError("HttpClientManager must init by infra.")
        resources = {
            k: HttpClient(conf, f"http_client{k}") for k, conf in confs.items()
        }
        super().__init__(resources, CTXKey.CLIENT_HTTP, error=HttpClientError)

    @property
    def curr(self) -> HttpClient:
        return super().curr


@InfraFactory.register(ConfKey.HTTP_CLIENT)
def _(conf):
    return HttpClientManager(conf)
