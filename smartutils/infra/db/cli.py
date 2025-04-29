from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Union

from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker

from smartutils.config.schema.mysql import MySQLConf
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.infra.abstract import AbstractResource
from smartutils.log import logger


class AsyncDBCli(AbstractResource):
    def __init__(self, conf: Union[MySQLConf, PostgreSQLConf], name: str):
        self._name = name
        kw = conf.kw
        kw['pool_reset_on_return'] = 'rollback'
        kw['pool_pre_ping'] = True
        kw['future'] = True

        self._engine: Union[Engine, AsyncEngine] = create_async_engine(conf.url, **kw)
        self._session = sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def ping(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.warning(f"[{self._name}] DB ping failed: {e}")
            return False

    async def close(self):
        await self._engine.dispose()

    @asynccontextmanager
    async def session(self):
        async with self._session() as session:
            yield session

    @property
    def engine(self):
        return self._engine

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        session = self._session()
        try:
            yield session
        finally:
            await session.close()

    async def create_tables(self, bases):
        async with self.engine.begin() as conn:
            for base in bases:
                await conn.run_sync(base.metadata.create_all)


async def db_commit(session: AsyncSession):
    if hasattr(session, "in_transaction") and session.in_transaction():
        await session.commit()
        logger.info(f'auto commit')


async def db_rollback(session: AsyncSession):
    if hasattr(session, "in_transaction") and session.in_transaction():
        await session.rollback()
        logger.info(f'auto rollback')
