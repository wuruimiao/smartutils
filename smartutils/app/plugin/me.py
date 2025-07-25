from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Optional, Tuple

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.auth.token import TokenHelper, User
from smartutils.app.const import MiddlewarePluginOrder
from smartutils.app.plugin.abstract import AuthBase
from smartutils.app.plugin.common import CustomHeader
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import (
    MiddlewarePluginKey,
    MiddlewarePluginSetting,
)
from smartutils.error.sys import LibraryUsageError, UnauthorizedError

try:
    from httpx import Response
except ImportError:
    pass

if TYPE_CHECKING:
    from httpx import Response


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.ME, order=MiddlewarePluginOrder.ME
)
class MePlugin(AuthBase, AbstractMiddlewarePlugin):
    def __init__(self, *, conf: MiddlewarePluginSetting):
        super().__init__(conf=conf, plugin_conf=conf.me)

        try:
            if self._conf.me.local:
                self._token_helper = TokenHelper()
        except LibraryUsageError:
            raise LibraryUsageError(f"{self.name} requires token in config.yaml.")

    async def _remote(self, req: RequestAdapter) -> Tuple[Optional[User], str]:
        # TODO：支持grpc服务
        cookies, msg = self.mk_cookies(req)
        if msg:
            return None, msg

        resp: Response = await self._client.me(cookies=cookies)
        data, msg = self._client.check_resp(resp)
        if msg:
            return None, msg

        if not data:
            return None, "no data."

        user = User(data["userid"], data["username"])
        return user, ""

    async def _local(self, req: RequestAdapter) -> Tuple[Optional[User], str]:
        access_token, msg = self.access_token(req)
        if msg:
            return None, msg

        user = self._token_helper.verify_access_token(access_token)
        return user, "" if user else "verify token failed."

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        if self._plugin_conf.local:
            user, msg = await self._local(req)
        else:
            user, msg = await self._remote(req)

        if msg or not user:
            return self._resp_fn(UnauthorizedError(f"{self.name} {msg}").as_dict)

        CustomHeader.userid(req, user.id)
        CustomHeader.username(req, user.name)

        resp: ResponseAdapter = await next_adapter()
        return resp
