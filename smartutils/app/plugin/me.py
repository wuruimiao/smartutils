from typing import Awaitable, Callable, cast

from httpx import Response

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import MiddlewarePluginOrder
from smartutils.app.plugin.common import CustomHeader, get_auth_cookies
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.const import ConfKey
from smartutils.config.schema.middleware import MiddlewarePluginKey
from smartutils.error.sys import (
    LibraryError,
    LibraryUsageError,
    SysError,
    UnauthorizedError,
)
from smartutils.infra.client.http import HttpClient
from smartutils.infra.client.manager import ClientManager


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.ME, order=MiddlewarePluginOrder.ME
)
class MePlugin(AbstractMiddlewarePlugin):
    def _init_client(self):
        if hasattr(self, "_client"):
            return

        try:
            self._client = cast(HttpClient, ClientManager().client(ConfKey.AUTH))
        except LibraryError:
            raise LibraryUsageError(
                "AuthPlugin depend on 'auth' below client in config.yaml."
            )

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        # TODO：支持grpc服务
        self._init_client()

        cookies = get_auth_cookies(req)
        if not cookies:
            return self._resp_fn(
                UnauthorizedError("AuthPlugin request no cookies").as_dict
            )

        me_resp: Response = await self._client.me(cookies=cookies)
        if me_resp.status_code != 200:
            return self._resp_fn(
                SysError(f"AuthPlugin me, return {me_resp.status_code}").as_dict
            )

        try:
            data = me_resp.json()
        except ValueError:
            return self._resp_fn(
                SysError(f"AuthPlugin me, return data not json. {me_resp.text}").as_dict
            )

        if data["code"] != 0:
            return self._resp_fn(UnauthorizedError(data["msg"]).as_dict)

        data = data["data"]
        CustomHeader.userid(req, data["userid"])
        CustomHeader.username(req, data["username"])

        resp: ResponseAdapter = await next_adapter()
        return resp
