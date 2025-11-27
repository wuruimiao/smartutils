from typing import List

from pydantic import BaseModel, Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory


@ConfFactory.register(ConfKey.ALERT_FEISHU, multi=False, require=False)
class AlertFeishuConf(BaseModel):
    enable: bool = Field(default=True, description="是否启用飞书告警")
    webhooks: List[str] = Field(..., description="通知链接")
