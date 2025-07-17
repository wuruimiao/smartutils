from typing import Awaitable, Callable, cast

from httpx import Response

from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey, MiddlewarePluginOrder
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
    MiddlewarePluginKey.AUTH, order=MiddlewarePluginOrder.AUTH
)
class AuthPlugin(AbstractMiddlewarePlugin):
    def __init__(self, app_key: AppKey):
        try:
            self._client: HttpClient = cast(
                HttpClient, ClientManager().client(ConfKey.AUTH)
            )
        except LibraryError:
            raise LibraryUsageError(
                "AuthPlugin depend on 'auth' below client in config.yaml."
            )
        self._resp_fn = JsonRespFactory.get(app_key)

        super().__init__(app_key)

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        # TODO: access_token配置化
        # TODO：支持grpc服务
        access_token = "access_token"
        value = req.get_cookie(access_token)
        if not value:
            return self._resp_fn(
                UnauthorizedError(f"AuthPlugin get request no {access_token}").as_dict
            )

        me_resp: Response = await self._client.me(cookies={access_token: value})
        if me_resp.status_code != 200:
            return self._resp_fn(
                SysError(f"AuthPlugin auth me, return {me_resp.status_code}").as_dict
            )

        try:
            data = me_resp.json()
        except ValueError:
            return self._resp_fn(
                SysError(f"AuthPlugin auth me, return data. {me_resp.text}").as_dict
            )

        if data["code"] != 0:
            return self._resp_fn(UnauthorizedError(data["msg"]).as_dict)

        resp: ResponseAdapter = await next_adapter()
        return resp
