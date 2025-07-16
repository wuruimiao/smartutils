from unittest.mock import AsyncMock

import pytest

from smartutils.config.schema.alert_feishu import AlertFeishuConf
from smartutils.infra.alert.feishu import AlertFeishu


@pytest.fixture(scope="function")
async def setup_config(tmp_path_factory):
    config_str = """
alert_feishu:
  enable: true
  webhooks:
    - http://example.com/webhook1
project:
  name: testproj
  id: 1
  description: http test
  version: 1.0.0
  key: test_key
"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)
    from smartutils.init import init

    await init(str(config_file))
    yield


async def test_alert_feishu_manager(setup_config):
    from smartutils.infra.alert.feishu import AlertFeishuManager

    mgr = AlertFeishuManager()
    for client in mgr.client()._clients:
        client.send_alert = AsyncMock(
            return_value=type("Resp", (), {"status_code": 200})()
        )

    results = await mgr.client().alert("title", "content")
    assert results == [True]


async def test_alert_feishu_alert_success():
    conf = AlertFeishuConf(enable=True, webhooks=["https://foo.com/abc123"])
    alert = AlertFeishu(conf)

    # mock所有client
    for client in alert._clients:
        client.send_alert = AsyncMock(
            return_value=type("Resp", (), {"status_code": 200})()
        )

    results = await alert.alert("title", "content")
    assert results == [True]


async def test_alert_feishu_alert_failure():
    conf = AlertFeishuConf(enable=True, webhooks=["https://foo.com/abc123"])
    alert = AlertFeishu(conf)

    # mock失败
    for client in alert._clients:
        client.send_alert = AsyncMock(
            return_value=type("Resp", (), {"status_code": 400})()
        )

    results = await alert.alert("ERRtitle", "ERRcontent")
    assert results == [False]


async def test_alert_feishu_close_calls_clients():
    conf = AlertFeishuConf(enable=True, webhooks=["https://foo.com/abc123"])
    alert = AlertFeishu(conf)
    for client in alert._clients:
        client.close = AsyncMock()

    await alert.close()
    for client in alert._clients:
        client.close.assert_awaited()


async def test_alert_feishu_ping():
    conf = AlertFeishuConf(enable=True, webhooks=["https://foo.com/abc123"])
    alert = AlertFeishu(conf)

    result = await alert.ping()
    assert result is True


async def test_alert_feishu_alert_disable():
    conf = AlertFeishuConf(enable=False, webhooks=["https://foo.com/abc123"])
    alert = AlertFeishu(conf)
    results = await alert.alert("title", "content")
    assert results == []
