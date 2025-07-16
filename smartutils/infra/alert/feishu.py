import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.alert_feishu import AlertFeishuConf
from smartutils.config.schema.client_http import ClientHttpConf, HttpApiConf
from smartutils.ctx.const import CTXKey
from smartutils.ctx.manager import CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import LibraryUsageError
from smartutils.infra.client.http import HttpClient
from smartutils.infra.factory import InfraFactory
from smartutils.infra.source_manager.abstract import AbstractResource
from smartutils.infra.source_manager.manager import CTXResourceManager
from smartutils.time import get_now_str


class AlertFeishu(AbstractResource):
    def __init__(self, conf: AlertFeishuConf):
        self._conf = conf
        self._clients = []
        if not conf.enable:
            return

        for webhook_url in conf.webhooks:
            http_conf = ClientHttpConf(
                endpoint=webhook_url,
                timeout=5,
                verify_tls=True,
                apis={"send_alert": HttpApiConf(path="", method="POST", timeout=5)},
            )
            self._clients.append(
                HttpClient(http_conf, name=f"feishu_{id(webhook_url)}")
            )

    async def alert(self, title: str, content: str):
        if not self._conf.enable or not self._clients:
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

    async def close(self):
        for client in self._clients:
            await client.close()

    async def ping(self) -> bool:
        return True

    @asynccontextmanager
    async def db(self, use_transaction: bool):
        yield self


@singleton
@CTXVarManager.register(CTXKey.ALERT_FEISHU)
class AlertFeishuManager(CTXResourceManager[AlertFeishu]):
    def __init__(self, conf: Optional[AlertFeishuConf] = None):
        if not conf:
            raise LibraryUsageError("AlertFeishuManager must init by infra.")
        resources = {ConfKey.GROUP_DEFAULT: AlertFeishu(conf)}
        super().__init__(resources, CTXKey.CLIENT_HTTP)

    @property
    def curr(self) -> AlertFeishu:
        return super().curr


@InfraFactory.register(ConfKey.ALERT_FEISHU)
def _(conf):
    return AlertFeishuManager(conf)
