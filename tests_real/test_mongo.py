import pytest

from smartutils.error.sys import DatabaseError, LibraryUsageError

pytestmark = pytest.mark.asyncio


@pytest.fixture
def test_coll():
    return "test_mongo_coll"


@pytest.fixture
def valid_mongo():
    yield


@pytest.fixture
async def unreachable_mongo(tmp_path_factory):
    mongo_config_unreachable_str = """
mongo:
  default:
    hosts:
      - host: 222.222.222.222
        port: 27017
    user: testuser
    passwd: testpass
    db: test_db
    connect: true
    connect_timeout: 2
    execute_timeout: 2
project:
  name: test_proj2
  id: 0
  description: mongo_unreachable
  version: 0.0.1
  key: test_key2
"""
    tmp_dir = tmp_path_factory.mktemp("badconf_mongo")
    config_file = tmp_dir / "unreachable_config.yaml"
    with open(config_file, "w") as f:
        f.write(mongo_config_unreachable_str)
    from smartutils.init import reset_all

    await reset_all()
    from smartutils.init import init

    await init(str(config_file))


async def test_mongo_manager_no_confs():
    from smartutils.init import reset_all

    await reset_all()
    from smartutils.infra import MongoManager

    with pytest.raises(LibraryUsageError):
        MongoManager()


async def test_mongo_client_ping(valid_mongo):
    from smartutils.infra import MongoManager

    mgr = MongoManager()
    cli = mgr.client()
    assert await cli.ping() is True


async def test_mongo_insert(valid_mongo, test_coll):
    from smartutils.infra import MongoManager

    mgr = MongoManager()
    doc = {"name": "testdoc", "value": 1024}

    @mgr.use()
    async def insert_one():
        ret = await mgr.curr[test_coll].insert_one(doc)
        assert ret.inserted_id is not None
        return ret.inserted_id

    inserted_id = await insert_one()
    return inserted_id


async def test_mongo_find(valid_mongo, test_coll):
    from smartutils.infra import MongoManager

    mgr = MongoManager()
    doc = {"name": "testdoc", "value": 1024}
    inserted_id = await test_mongo_insert(valid_mongo, test_coll)

    @mgr.use
    async def find_one():
        obj = await mgr.curr[test_coll].find_one({"_id": inserted_id})
        assert obj is not None
        assert obj["name"] == "testdoc"
        return obj

    found = await find_one()
    return inserted_id, found


async def test_mongo_update(valid_mongo, test_coll):
    from smartutils.infra import MongoManager

    mgr = MongoManager()
    inserted_id, _ = await test_mongo_find(valid_mongo, test_coll)

    @mgr.use
    async def update_one():
        res = await mgr.curr[test_coll].update_one(
            {"_id": inserted_id}, {"$set": {"value": 2048}}
        )
        assert res.modified_count == 1

    await update_one()

    @mgr.use()
    async def check_upd():
        obj = await mgr.curr[test_coll].find_one({"_id": inserted_id})
        assert obj["value"] == 2048  # type: ignore

    await check_upd()
    return inserted_id


async def test_mongo_delete(valid_mongo, test_coll):
    from smartutils.infra import MongoManager

    mgr = MongoManager()
    inserted_id = await test_mongo_update(valid_mongo, test_coll)

    @mgr.use()
    async def delete_one():
        res = await mgr.curr[test_coll].delete_one({"_id": inserted_id})
        assert res.deleted_count == 1

    await delete_one()

    @mgr.use()
    async def confirm_del():
        obj = await mgr.curr[test_coll].find_one({"_id": inserted_id})
        assert obj is None

    await confirm_del()


async def test_mongo_ping_fail(unreachable_mongo):
    from smartutils.infra import MongoManager

    cli = MongoManager().client()
    assert await cli.ping() is False


async def test_mongo_manager_use_unreachable(unreachable_mongo, test_coll):

    from smartutils.infra import MongoManager

    mgr = MongoManager()

    @mgr.use()
    async def try_insert():
        await mgr.curr.insert_one(test_coll, {"key": "value"})

    with pytest.raises(DatabaseError):
        await try_insert()
