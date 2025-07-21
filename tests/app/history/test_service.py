from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture(scope="function", autouse=True)
async def setup_config(tmp_path_factory):
    config_str = """
mysql:
  default:
    host: localhost
    port: 3306
    user: root
    passwd: naobo
    db: test_db
    pool_size: 10
    max_overflow: 5
    pool_timeout: 30
    pool_recycle: 3600
    echo: false
    echo_pool: false
    connect_timeout: 10
    execute_timeout: 10
project:
  name: auth
  id: 0
  description: test_auth
  version: 0.0.1
  key: test_key"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    from smartutils.patch import patched_manager_with_mocked_dbcli

    with patched_manager_with_mocked_dbcli("smartutils.infra.db.mysql.AsyncDBCli") as (
        MockDBCli,
        fake_session,
        instance,
    ):
        from smartutils.infra.db import mysql

        assert isinstance(mysql.AsyncDBCli, MagicMock)
        from smartutils.init import init

        init(str(config_file))
        yield {
            "fake_session": fake_session,
            "MockDBCli": MockDBCli,
            "instance": instance,
        }


@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    import smartutils.app.history.service as mod

    fake_db = MagicMock()
    fake_db.curr = MagicMock()
    monkeypatch.setattr(mod, "db", fake_db)


class _OpType:
    ADD = MagicMock(value=1)
    UPDATE = MagicMock(value=3)


@pytest.fixture
def fake_OpType(monkeypatch):
    import smartutils.app.history.service as mod

    monkeypatch.setattr(mod, "OpType", _OpType)


async def test_record_history(fake_OpType):
    import smartutils.app.history.service as mod

    mod.db.curr.add = MagicMock()
    await mod.op_history_controller.record_history(
        "A", 1, _OpType.ADD, 99, {"a": 1}, {"b": 2}
    )
    mod.db.curr.add.assert_called()


async def test_get_op_id_by_order_basic(monkeypatch, fake_OpType):
    import smartutils.app.history.service as mod

    mod.db.curr.execute = AsyncMock()
    fake_row = MagicMock()
    fake_row.fetchall.return_value = [(2, 10), (3, 20)]
    mod.db.curr.execute.return_value = fake_row
    ids = await mod.op_history_controller.get_op_id_by_order(
        "A", [2, 3], "asc", _OpType.ADD
    )
    assert ids == {2: 10, 3: 20}
    ids = await mod.op_history_controller.get_op_id_by_order("A", [], "asc")
    assert ids == {}


async def test_get_op_id_by_order_desc(monkeypatch, fake_OpType):
    import smartutils.app.history.service as mod

    mod.db.curr.execute = AsyncMock()
    fake_row = MagicMock()
    fake_row.fetchall.return_value = [(4, 30)]
    mod.db.curr.execute.return_value = fake_row
    ids = await mod.op_history_controller.get_op_id_by_order(
        "A", [4], "desc", _OpType.UPDATE
    )
    assert ids == {4: 30}


async def test_get_creator_id_and_last_updator_id(fake_OpType, monkeypatch):
    import smartutils.app.history.service as mod

    # MagicMock而不是AsyncMock
    fake_row = MagicMock()
    fake_row.fetchall = MagicMock(return_value=[(8, 33)])
    mod.db.curr.execute = AsyncMock(return_value=fake_row)
    called = {}

    async def fake_op_order(*a, **kw):
        called["order"] = (a, kw)
        return {8: 33}

    monkeypatch.setattr(mod.op_history_controller, "get_op_id_by_order", fake_op_order)
    ret1 = await mod.op_history_controller.get_creator_id("T", [8])
    assert ret1 == {8: 33}
    ret2 = await mod.op_history_controller.get_last_updator_id("T", [8])
    assert ret2 == {8: 33}


async def test_get_creator_and_last_updator_id_normal(monkeypatch, fake_OpType):
    import smartutils.app.history.service as mod

    mod.db.curr.execute = AsyncMock()
    fake_row = MagicMock()
    fake_row.fetchall.return_value = [
        (101, 1001, 1, 1, None),  # creator
        (101, 2002, 3, None, 1),  # updator
    ]
    mod.db.curr.execute.return_value = fake_row
    res = await mod.op_history_controller.get_creator_and_last_updator_id("TT", [101])
    assert (res[101].creator_id, res[101].updator_id) == (1001, 2002)
    emp = await mod.op_history_controller.get_creator_and_last_updator_id("AA", [])
    assert emp == {}


async def test_get_op_ids(monkeypatch):
    import smartutils.app.history.service as mod

    mod.db.curr.execute = AsyncMock()
    fake_row = MagicMock()
    fake_row.fetchall.return_value = [(9, 111), (9, 112), (10, 120)]
    mod.db.curr.execute.return_value = fake_row
    ret = await mod.op_history_controller.get_op_ids("BT", [9, 10])
    assert dict(ret) == {9: [111, 112], 10: [120]}
    emp = await mod.op_history_controller.get_op_ids("BT", [])
    assert dict(emp) == {}


async def test_BizOpInfo_all(monkeypatch, fake_OpType):
    import smartutils.app.history.service as mod

    handler = AsyncMock()

    class User:
        def __init__(self, name):
            self.real_name = name

    userDict = {1: User("zh"), 2: User("xi")}
    handler.return_value = userDict

    async def fake_creator_last(*a, **kw):
        return {99: mod.OpUser(creator_id=1, updator_id=2)}

    monkeypatch.setattr(
        mod.op_history_controller, "get_creator_and_last_updator_id", fake_creator_last
    )
    boi = mod.BizOpInfo("B", [99], handler)
    await boi.init()
    s = str(boi)
    # 仅断言结构存在
    assert "biz=B" in s and "ops={99: OpUser(creator_id=1, updator_id=2)}" in s
    assert boi.biz_creator_attr(99) == "zh"
    assert boi.biz_updator_attr(99) == "xi"
    # biz_id/用户缺失分支
    assert boi.biz_creator_attr(88) == ""
    boi._user_infos.pop(1)
    assert boi.biz_creator_attr(99) == ""
    boi._user_infos[1] = "changed"
    boi._biz_ops = {}
    assert boi.biz_creator_attr(99) == ""
