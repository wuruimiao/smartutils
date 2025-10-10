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
    from smartutils.init import init

    init(str(config_file))
    yield


@pytest.fixture(autouse=True)
def patch_db(mocker):
    mock_class = mocker.Mock()
    mock_class.return_value.method.return_value = "mocked"
    mocker.patch("smartutils.app.history.service.MySQLManager", mock_class)


async def test_record_history(mocker):
    import smartutils.app.history.service as mod

    mod.get_db().curr.add = mocker.MagicMock()
    await mod.op_history_controller.record_history(
        "A", 1, mod.OpType.ADD, 99, {"a": 1}, {"b": 2}
    )
    mod.get_db().curr.add.assert_called()  # type: ignore


async def test_get_op_id_by_order_basic(mocker):
    import smartutils.app.history.service as mod

    mod.get_db().curr.execute = mocker.AsyncMock()
    fake_row = mocker.MagicMock()
    fake_row.fetchall.return_value = [(2, 10), (3, 20)]
    mod.get_db().curr.execute.return_value = fake_row  # type: ignore
    ids = await mod.op_history_controller.get_op_id_by_order(
        "A", [2, 3], "asc", mod.OpType.ADD
    )
    assert ids == {2: 10, 3: 20}
    ids = await mod.op_history_controller.get_op_id_by_order("A", [], "asc")
    assert ids == {}


async def test_get_op_id_by_order_desc(mocker):
    import smartutils.app.history.service as mod

    mod.get_db().curr.execute = mocker.AsyncMock()
    fake_row = mocker.MagicMock()
    fake_row.fetchall.return_value = [(4, 30)]
    mod.get_db().curr.execute.return_value = fake_row  # type: ignore
    ids = await mod.op_history_controller.get_op_id_by_order(
        "A", [4], "desc", mod.OpType.UPDATE
    )
    assert ids == {4: 30}


async def test_get_creator_id_and_last_updator_id(mocker):
    import smartutils.app.history.service as mod

    fake_row = mocker.MagicMock()
    fake_row.fetchall = mocker.MagicMock(return_value=[(8, 33)])
    mod.get_db().curr.execute = mocker.AsyncMock(return_value=fake_row)
    called = {}

    async def fake_op_order(*a, **kw):
        called["order"] = (a, kw)
        return {8: 33}

    mocker.patch.object(mod.op_history_controller, "get_op_id_by_order", fake_op_order)
    ret1 = await mod.op_history_controller.get_creator_id("T", [8])
    assert ret1 == {8: 33}
    ret2 = await mod.op_history_controller.get_last_updator_id("T", [8])
    assert ret2 == {8: 33}


async def test_get_creator_and_last_updator_id_normal(mocker):
    import smartutils.app.history.service as mod

    mod.get_db().curr.execute = mocker.AsyncMock()
    fake_row = mocker.MagicMock()
    fake_row.fetchall.return_value = [
        (101, 1001, 1, 1, None),
        (101, 2002, 3, None, 1),
    ]
    mod.get_db().curr.execute.return_value = fake_row  # type: ignore
    res = await mod.op_history_controller.get_creator_and_last_updator_id("TT", [101])
    assert (res[101].creator_id, res[101].updator_id) == (1001, 2002)
    emp = await mod.op_history_controller.get_creator_and_last_updator_id("AA", [])
    assert emp == {}


async def test_get_op_ids(mocker):
    import smartutils.app.history.service as mod

    mod.get_db().curr.execute = mocker.AsyncMock()
    fake_row = mocker.MagicMock()
    fake_row.fetchall.return_value = [(9, 111), (9, 112), (10, 120)]
    mod.get_db().curr.execute.return_value = fake_row  # type: ignore
    ret = await mod.op_history_controller.get_op_ids("BT", [9, 10])
    assert dict(ret) == {9: [111, 112], 10: [120]}
    emp = await mod.op_history_controller.get_op_ids("BT", [])
    assert dict(emp) == {}


async def test_BizOpInfo_all(mocker):
    import smartutils.app.history.service as mod

    handler = mocker.AsyncMock()

    class User:  # noqa
        def __init__(self, name):
            self.realname = name

    userDict = {1: User("zh"), 2: User("xi")}
    handler.return_value = userDict

    async def fake_creator_last(*a, **kw):
        return {99: mod.OpUser(creator_id=1, updator_id=2)}

    mocker.patch.object(
        mod.op_history_controller, "get_creator_and_last_updator_id", fake_creator_last
    )
    boi = mod.BizOpInfo("B", [99], handler)
    await boi.init()
    s = str(boi)
    assert "biz=B" in s and "ops={99: OpUser(creator_id=1, updator_id=2)}" in s
    assert boi.biz_creator_attr(99) == "zh"
    assert boi.biz_updator_attr(99) == "xi"
    assert boi.biz_creator_attr(88) == ""
    boi._user_infos.pop(1)
    assert boi.biz_creator_attr(99) == ""
    boi._user_infos[1] = "changed"
    boi._biz_ops = {}
    assert boi.biz_creator_attr(99) == ""
