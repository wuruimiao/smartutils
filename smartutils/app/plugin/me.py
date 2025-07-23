from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Dict, Optional, Tuple, cast

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.auth.token import TokenHelper
from smartutils.app.const import AppKey, MiddlewarePluginOrder
from smartutils.app.plugin.common import CustomHeader
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import (
    MiddlewarePluginKey,
    MiddlewarePluginSetting,
)
from smartutils.error.sys import SysError, UnauthorizedError
from smartutils.infra.client.http import HttpClient
from smartutils.infra.client.manager import ClientManager
from smartutils.init.mixin import LibraryCheckMixin

try:
    from httpx import Response
except ImportError:
    pass

if TYPE_CHECKING:
    from httpx import Response


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.ME, order=MiddlewarePluginOrder.ME
)
class MePlugin(LibraryCheckMixin, AbstractMiddlewarePlugin):
    def __init__(self, *, app_key: AppKey, conf: MiddlewarePluginSetting):
        super().__init__(app_key=app_key, conf=conf)

        self.check(require_conf=False, libs=["httpx"])
        self._client = cast(
            HttpClient, ClientManager().client(self._conf.me.client_key)
        )

    async def _get_user_by_client(
        self, access_token: str
    ) -> Tuple[Optional[Dict], Optional[ResponseAdapter]]:
        # TODO：支持grpc服务
        me_resp: Response = await self._client.me(
            cookies={self._conf.me.access_name: access_token}
        )
        data, msg = self._client.check_resp(me_resp)
        if msg:
            return None, self._resp_fn(UnauthorizedError(f"MePlugin {msg}").as_dict)

        return data, None

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        access_token = req.get_cookie(self._conf.me.access_name)
        if not access_token:
            return self._resp_fn(
                UnauthorizedError("MePlugin request no cookies").as_dict
            )

        if self._conf.me.access_secret:
            token_helper = TokenHelper()
            data = token_helper.verify_token(access_token, self._conf.me.access_secret)
            if not data:
                return self._resp_fn(
                    UnauthorizedError("MePlugin request token verify failed").as_dict
                )
        else:
            data, resp_ok = await self._get_user_by_client(access_token)
            if resp_ok:
                return resp_ok

        if not data:
            return self._resp_fn(SysError("MePlugin no data").as_dict)

        CustomHeader.userid(req, data["userid"])
        CustomHeader.username(req, data["username"])

        resp: ResponseAdapter = await next_adapter()
        return resp
