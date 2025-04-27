import pytest
from sqlalchemy import text

from sqlalchemy import Column, Integer, String

from smartutils.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64))


@pytest.fixture(scope="session", autouse=True)
async def setup_db(tmp_path_factory):
    config_str = """
mysql:
  host: 192.168.1.56
  port: 3306
  user: root
  passwd: naobo
  db: testdb

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
    print(config_file)

    from smartutils.db import init
    init()
    from smartutils.db import db
    await db.create_tables([Base])
    yield
    await db.close()


@pytest.mark.asyncio
async def test_get_db():
    from smartutils.db import db
    # 测试插入/查询/删除
    async for session in db.get_db():
        user = User(name="pytest")
        session.add(user)
        await session.commit()

        user2 = await session.get(User, user.id)
        assert user2.name == "pytest"

        await session.delete(user2)
        await session.commit()


@pytest.mark.asyncio
async def test_with_db_success_and_rollback():
    from smartutils.db import db

    @db.with_db
    async def insert_and_fail(name):
        session = db.curr_db()
        user = User(name=name)
        session.add(user)
        await session.flush()
        raise ValueError("fail")  # 模拟失败触发回滚

    # Should rollback, user not in db
    with pytest.raises(ValueError):
        await insert_and_fail("rollback_user")

    async for session in db.get_db():
        result = await session.execute(
            text("SELECT COUNT(*) FROM users WHERE name='rollback_user'")
        )
        assert result.scalar() == 0


@pytest.mark.asyncio
async def test_with_db_commit():
    from smartutils.db import db

    @db.with_db
    async def insert_user(name):
        session = db.curr_db()
        user = User(name=name)
        session.add(user)
        await session.flush()
        return user.id

    user_id = await insert_user("committed_user")
    async for session in db.get_db():
        u = await session.get(User, user_id)
        assert u.name == "committed_user"
        # 清理
        await session.delete(u)
        await session.commit()


@pytest.mark.asyncio
async def test_curr_db_no_context():
    from smartutils.db import db

    with pytest.raises(RuntimeError):
        db.curr_db()
