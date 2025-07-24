from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Dict, Optional, Tuple, cast

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.auth.token import TokenHelper, User
from smartutils.app.const import AppKey, MiddlewarePluginOrder
from smartutils.app.plugin.common import CustomHeader
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import (
    MiddlewarePluginKey,
    MiddlewarePluginSetting,
)
from smartutils.design import MyBase
from smartutils.error.sys import LibraryUsageError, SysError, UnauthorizedError
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
class MePlugin(LibraryCheckMixin, MyBase, AbstractMiddlewarePlugin):
    def __init__(self, *, app_key: AppKey, conf: MiddlewarePluginSetting):
        super().__init__(app_key=app_key, conf=conf)

        self.check(require_conf=False, libs=["httpx"])
        try:
            self._client = cast(
                HttpClient, ClientManager().client(self._conf.me.client_key)
            )
            if self._conf.me.local:
                self._token_helper = TokenHelper()
        except LibraryUsageError:
            raise LibraryUsageError(
                f"{self.name} requires auth below client and token in config.yaml."
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
            return None, self._resp_fn(UnauthorizedError(f"{self.name} {msg}").as_dict)

        return data, None

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        access_token = req.get_cookie(self._conf.me.access_name)
        if not access_token:
            return self._resp_fn(
                UnauthorizedError(f"{self.name} request no cookies").as_dict
            )

        user: Optional[User]
        if self._conf.me.local:
            user = self._token_helper.verify_access_token(access_token)
            if not user:
                return self._resp_fn(
                    UnauthorizedError(f"{self.name} verify token failed").as_dict
                )
        else:
            data, resp_ok = await self._get_user_by_client(access_token)
            if resp_ok:
                return resp_ok
            if not data:
                return self._resp_fn(SysError(f"{self.name} no data").as_dict)
            user = User(data["userid"], data["username"])

        CustomHeader.userid(req, user.id)
        CustomHeader.username(req, user.name)

        resp: ResponseAdapter = await next_adapter()
        return resp
