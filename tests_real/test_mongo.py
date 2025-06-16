import pytest

from smartutils.error.sys import DatabaseError, LibraryUsageError

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mongo_config_str():
    return """
mongo:
  default:
    hosts:
      - host: 192.168.1.56
        port: 27017
    user: root
    passwd: naobo
    db: test_db
    pool_size: 5
    pool_timeout: 10
    pool_recycle: 60
    connect: true
    connect_timeout: 3
    execute_timeout: 3
project:
  name: test_proj
  id: 0
  description: mongo_real_test
  version: 0.0.1
  key: test
"""


@pytest.fixture
def mongo_config_unreachable_str():
    # 明显错误IP
    return """
mongo:
  default:
    hosts:
      - host: 222.22.22.22
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


@pytest.fixture
def test_coll():
    return "test_mongo_coll"


@pytest.fixture
def valid_mongo_conf(tmp_path_factory, mongo_config_str):
    tmp_dir = tmp_path_factory.mktemp("config_mongo")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(mongo_config_str)
    return config_file


@pytest.fixture
def unreachable_mongo_conf(tmp_path_factory, mongo_config_unreachable_str):
    tmp_dir = tmp_path_factory.mktemp("badconf_mongo")
    config_file = tmp_dir / "unreachable_config.yaml"
    with open(config_file, "w") as f:
        f.write(mongo_config_unreachable_str)
    return config_file


async def test_mongo_manager_no_confs():
    from smartutils.infra import MongoManager

    with pytest.raises(LibraryUsageError):
        MongoManager()


async def test_mongo_client_ping(valid_mongo_conf):
    from smartutils.init import init

    await init(str(valid_mongo_conf))
    from smartutils.infra import MongoManager

    mgr = MongoManager()
    cli = mgr.client()
    assert await cli.ping() is True


async def test_mongo_crud(valid_mongo_conf, test_coll):
    from smartutils.init import init

    await init(str(valid_mongo_conf))
    from smartutils.infra import MongoManager

    mgr = MongoManager()
    doc = {"name": "testdoc", "value": 1024}

    # Insert
    @mgr.use()
    async def insert_one():
        ret = await mgr.curr.insert_one(test_coll, doc)
        assert ret.inserted_id is not None
        return ret.inserted_id

    inserted_id = await insert_one()

    # Find
    @mgr.use
    async def find_one():
        obj = await mgr.curr.find_one(test_coll, {"_id": inserted_id})
        assert obj is not None
        assert obj["name"] == "testdoc"
        return obj

    found = await find_one()

    # Update
    @mgr.use
    async def update_one():
        res = await mgr.curr.update_one(
            test_coll, {"_id": inserted_id}, {"$set": {"value": 2048}}
        )
        assert res.modified_count == 1

    await update_one()

    # Confirm Update
    @mgr.use()
    async def check_upd():
        obj = await mgr.curr.find_one(test_coll, {"_id": inserted_id})
        assert obj["value"] == 2048

    await check_upd()

    # Delete
    @mgr.use()
    async def delete_one():
        res = await mgr.curr.delete_one(test_coll, {"_id": inserted_id})
        assert res.deleted_count == 1

    await delete_one()

    # Confirm Delete
    @mgr.use()
    async def confirm_del():
        obj = await mgr.curr.find_one(test_coll, {"_id": inserted_id})
        assert obj is None

    await confirm_del()


async def test_mongo_ping_fail(unreachable_mongo_conf):
    from smartutils.init import init

    await init(str(unreachable_mongo_conf))
    from smartutils.infra import MongoManager

    cli = MongoManager().client()
    assert await cli.ping() is False


async def test_mongo_manager_use_unreachable(unreachable_mongo_conf, test_coll):
    from smartutils.init import init

    await init(str(unreachable_mongo_conf))
    from smartutils.infra import MongoManager

    mgr = MongoManager()

    @mgr.use()
    async def try_insert():
        await mgr.curr.insert_one(test_coll, {"key": "value"})

    with pytest.raises(DatabaseError):
        await try_insert()
