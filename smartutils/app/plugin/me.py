from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Dict, Optional, Tuple, cast

try:
    from httpx import Response
except ImportError:
    pass

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.auth.token import TokenHelper
from smartutils.app.const import MiddlewarePluginOrder
from smartutils.app.plugin.common import CustomHeader
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

if TYPE_CHECKING:
    from httpx import Response


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.ME, order=MiddlewarePluginOrder.ME
)
class MePlugin(AbstractMiddlewarePlugin):
    def _init_client(self):
        assert (
            Response
        ), "smartutils.app.plugin.me.MePlugin depend on httpx, install before use"
        if hasattr(self, "_client"):
            return

        try:
            self._client = cast(
                HttpClient, ClientManager().client(ConfKey(self._conf.me.client_key))
            )
        except LibraryError:
            raise LibraryUsageError(
                "AuthPlugin depend on 'auth' below client in config.yaml."
            )

    async def _get_user_by_client(
        self, access_token: str
    ) -> Tuple[Dict, Optional[ResponseAdapter]]:
        # TODO：支持grpc服务
        self._init_client()

        me_resp: Response = await self._client.me(
            cookies={self._conf.me.access_name: access_token}
        )
        if me_resp.status_code != 200:
            return {}, self._resp_fn(
                SysError(f"AuthPlugin me, return {me_resp.status_code}").as_dict
            )

        try:
            data = me_resp.json()
        except ValueError:
            return {}, self._resp_fn(
                SysError(f"AuthPlugin me, return data not json. {me_resp.text}").as_dict
            )

        if data["code"] != 0:
            return {}, self._resp_fn(UnauthorizedError(data["msg"]).as_dict)

        data = data["data"]
        return data, None

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        access_token = req.get_cookie(self._conf.me.access_name)
        if not access_token:
            return self._resp_fn(
                UnauthorizedError("AuthPlugin request no cookies").as_dict
            )

        if self._conf.me.access_secret:
            token_helper = TokenHelper()
            data = token_helper.verify_token(access_token, self._conf.me.access_secret)
            if not data:
                return self._resp_fn(
                    UnauthorizedError("AuthPlugin request token verify failed").as_dict
                )
        else:
            data, resp_ok = await self._get_user_by_client(access_token)
            if resp_ok:
                return resp_ok

        CustomHeader.userid(req, data["userid"])
        CustomHeader.username(req, data["username"])

        resp: ResponseAdapter = await next_adapter()
        return resp
