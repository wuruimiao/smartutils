import asyncio
import sys
from contextlib import asynccontextmanager
from typing import Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.alert_feishu import AlertFeishuConf
from smartutils.config.schema.client import ApiConf, ClientConf, ClientType
from smartutils.ctx.const import CTXKey
from smartutils.ctx.manager import CTXVarManager
from smartutils.design import SingletonMeta
from smartutils.infra.client.http import HttpClient
from smartutils.infra.resource.abstract import AbstractAsyncResource
from smartutils.infra.resource.manager.manager import CTXResourceManager
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger
from smartutils.time import get_now_str

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override


class AlertFeishu(AbstractAsyncResource):
    def __init__(self, conf: AlertFeishuConf):
        self._conf = conf
        self._clients = []
        if not conf.enable:
            return

        for webhook_url in conf.webhooks:
            http_conf = ClientConf(
                type=ClientType.HTTP,
                endpoint=webhook_url,
                timeout=5,
                verify_tls=True,
                apis={"send_alert": ApiConf(path="", method="POST", timeout=5)},
            )
            self._clients.append(
                HttpClient(http_conf, name=f"alert_feishu_{webhook_url}")
            )

    async def alert(self, title: str, content: str):
        if not self._conf.enable or not self._clients:
            logger.info("AlertFeishu is disabled or no clients")
            return []

        now = get_now_str()
        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": f"🚨告警: {title}",
                        "content": [
                            [
                                {"tag": "text", "text": "内容："},
                                {"tag": "text", "text": content},
                            ],
                            [
                                {"tag": "text", "text": "时间："},
                                {"tag": "text", "text": now},
                            ],
                        ],
                    }
                }
            },
        }

        async def send_one(client):
            try:
                resp = await client.send_alert(json=payload)
                return resp.status_code == 200
            except Exception:
                return False

        return await asyncio.gather(
            *[send_one(client) for client in self._clients], return_exceptions=False
        )

    @override
    async def close(self):
        for client in self._clients:
            await client.close()

    @override
    async def ping(self) -> bool:
        return True

    @asynccontextmanager
    async def acquire(self, use_transaction: bool):
        yield self


CTXVarManager.register_v(CTXKey.ALERT_FEISHU)


class AlertFeishuManager(
    LibraryCheckMixin, CTXResourceManager[AlertFeishu], metaclass=SingletonMeta
):
    def __init__(self, conf: Optional[AlertFeishuConf] = None):
        self.check(conf=conf)
        assert conf is not None

        resources = {ConfKey.GROUP_DEFAULT.value: AlertFeishu(conf)}
        super().__init__(resources=resources, ctx_key=CTXKey.ALERT_FEISHU)


@InitByConfFactory.register(ConfKey.ALERT_FEISHU)
def _(_, conf):
    return AlertFeishuManager(conf)
