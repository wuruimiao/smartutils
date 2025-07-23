from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, cast

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey, MiddlewarePluginOrder
from smartutils.app.plugin.common import CustomHeader, get_auth_cookies
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
    MiddlewarePluginKey.PERMISSION, order=MiddlewarePluginOrder.PERMISSION
)
class PermissionPlugin(LibraryCheckMixin, AbstractMiddlewarePlugin):
    def __init__(self, *, app_key: AppKey, conf: MiddlewarePluginSetting):
        super().__init__(app_key=app_key, conf=conf)

        self.check(require_conf=False, libs=["httpx"])
        self._client = cast(
            HttpClient,
            ClientManager().client(self._conf.permission.client_key),
        )

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        cookies = get_auth_cookies(req, self._conf.permission.access_name)
        if not cookies:
            return self._resp_fn(
                UnauthorizedError("PermissionPlugin request no cookies").as_dict
            )

        p_resp: Response = await self._client.permission(
            cookies=cookies, params={"api": req.path}
        )
        data, msg = self._client.check_resp(p_resp)
        if msg:
            return self._resp_fn(UnauthorizedError(f"PermissionPlugin {msg}").as_dict)
        if not data:
            return self._resp_fn(SysError("PermissionPlugin no data").as_dict)

        if not data["can_access"]:
            return self._resp_fn(UnauthorizedError(data["no permission"]).as_dict)

        CustomHeader.permission_user_ids(req, data["user_ids"])

        resp: ResponseAdapter = await next_adapter()
        return resp
