async def test_real_alert_feishu():
    from smartutils.infra.alert.feishu import AlertFeishuManager

    mgr = AlertFeishuManager()
    results = await mgr.client().alert("单元测试", "这是单元测试内容")
    assert results == [True]
