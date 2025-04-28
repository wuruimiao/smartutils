import pytest
from sqlalchemy import text

from sqlalchemy import Column, Integer, String

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64))


@pytest.fixture(scope="function", autouse=True)
async def setup_db(tmp_path_factory):
    config_str = """
mysql:
  default:
    host: 127.0.0.1
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
    execute_timeout: 10"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    from smartutils.config import init
    init(str(config_file))

    from smartutils.infra import init
    await init()

    from smartutils.infra import MySQLManager
    my_mgr = MySQLManager()
    await my_mgr.client().create_tables([Base])
    yield
    await my_mgr.close()

    from smartutils.design.singleton import reset_all
    reset_all()


@pytest.mark.asyncio
async def test_get_db():
    from smartutils.infra import MySQLManager
    my_mgr = MySQLManager()
    # 测试插入/查询/删除
    async for session in my_mgr.client().get_db():
        user = User(name="pytest")
        session.add(user)
        await session.commit()

        user2 = await session.get(User, user.id)
        assert user2.name == "pytest"

        await session.delete(user2)
        await session.commit()


@pytest.mark.asyncio
async def test_with_db_success_and_rollback():
    from smartutils.infra import MySQLManager
    my_mgr = MySQLManager()

    @my_mgr.use()
    async def insert_and_fail(name):
        session = my_mgr.curr()
        user = User(name=name)
        session.add(user)
        await session.flush()
        raise ValueError("fail")  # 模拟失败触发回滚

    # Should rollback, user not in db
    with pytest.raises(RuntimeError) as exc:
        await insert_and_fail("default use err")
    assert isinstance(exc.value.__cause__, ValueError)

    async for session in my_mgr.client().get_db():
        result = await session.execute(
            text("SELECT COUNT(*) FROM users WHERE name='rollback_user'")
        )
        assert result.scalar() == 0


@pytest.mark.asyncio
async def test_with_db_commit():
    from smartutils.infra import MySQLManager
    my_mgr = MySQLManager()

    @my_mgr.use()
    async def insert_user(name):
        session = my_mgr.curr()
        user = User(name=name)
        session.add(user)
        await session.flush()
        return user.id

    user_id = await insert_user("committed_user")
    async for session in my_mgr.client().get_db():
        u = await session.get(User, user_id)
        assert u.name == "committed_user"
        # 清理
        await session.delete(u)
        await session.commit()


@pytest.mark.asyncio
async def test_curr_db_no_context():
    from smartutils.infra import MySQLManager
    my_mgr = MySQLManager()

    with pytest.raises(RuntimeError):
        my_mgr.curr()
