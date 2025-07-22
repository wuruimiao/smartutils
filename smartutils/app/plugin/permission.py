from typing import TYPE_CHECKING, Awaitable, Callable, cast

try:
    from httpx import Response
except ImportError:
    pass

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

if TYPE_CHECKING:
    from httpx import Response


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.PERMISSION, order=MiddlewarePluginOrder.PERMISSION
)
class PermissionPlugin(AbstractMiddlewarePlugin):
    def _init_client(self):
        assert (
            Response
        ), "smartutils.app.plugin.permission.PermissionPlugin depend on httpx, install before use"
        if hasattr(self, "_client"):
            return
        try:
            self._client = cast(
                HttpClient,
                ClientManager().client(ConfKey(self._conf.permission.client_key)),
            )
        except LibraryError:
            raise LibraryUsageError(
                "PermissionPlugin depend on 'auth' below client in config.yaml."
            )

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        self._init_client()

        cookies = get_auth_cookies(req, self._conf.permission.access_name)
        if not cookies:
            return self._resp_fn(
                UnauthorizedError("PermissionPlugin request no cookies").as_dict
            )

        p_resp: Response = await self._client.permission(
            cookies=cookies, params={"api": req.path}
        )
        if p_resp.status_code != 200:
            return self._resp_fn(
                SysError(
                    f"PermissionPlugin auth permission, return {p_resp.status_code}"
                ).as_dict
            )

        try:
            data = p_resp.json()
        except ValueError:
            return self._resp_fn(
                SysError(
                    f"PermissionPlugin auth permission, return data not json. {p_resp.text}"
                ).as_dict
            )

        if data["code"] != 0:
            return self._resp_fn(UnauthorizedError(data["msg"]).as_dict)

        data = data["data"]
        if not data["can_access"]:
            return self._resp_fn(UnauthorizedError(data["no permission"]).as_dict)

        CustomHeader.permission_user_ids(req, data["user_ids"])

        resp: ResponseAdapter = await next_adapter()
        return resp
