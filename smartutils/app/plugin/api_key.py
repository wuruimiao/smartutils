import hashlib
from typing import Awaitable, Callable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import HeaderKey, MiddlewarePluginOrder
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import MiddlewarePluginKey
from smartutils.error.sys import UnauthorizedError

__all__ = ["ApiKeyPlugin"]

key = MiddlewarePluginKey.APIKEY


def calc_signature(key: str, timestamp: str, secret: str):
    plain = f"key={key}&timestamp={timestamp}&secret={secret}"
    return hashlib.sha256(plain.encode()).hexdigest()


@MiddlewarePluginFactory.register(key, order=MiddlewarePluginOrder.APIKEY)
class ApiKeyPlugin(AbstractMiddlewarePlugin):
    _key = key

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        api_key = req.get_header(HeaderKey(self._conf.api_key.header_key))
        if api_key not in self._conf.api_key.keys:
            return self._resp_fn(
                UnauthorizedError(
                    f"ApiKeyPlugin invalid key, received: {api_key}"
                ).as_dict
            )

        if self._conf.api_key.secret:
            signature = req.get_header(HeaderKey(self._conf.api_key.header_signature))
            timestamp = req.get_header(HeaderKey(self._conf.api_key.header_timestamp))
            if not signature or not timestamp:
                return self._resp_fn(
                    UnauthorizedError(
                        "ApiKeyPlugin missing signature or timestamp"
                    ).as_dict
                )
            expected_sign = calc_signature(
                api_key, timestamp, self._conf.api_key.secret
            )
            if signature != expected_sign:
                return self._resp_fn(
                    UnauthorizedError("ApiKeyPlugin invalid signature").as_dict
                )

        resp: ResponseAdapter = await next_adapter()
        return resp
