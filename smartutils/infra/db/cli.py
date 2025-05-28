from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Union

from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from smartutils.config.schema.mysql import MySQLConf
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.infra.source_manager.abstract import AbstractResource
from smartutils.log import logger

__all__ = ["AsyncDBCli", "db_commit", "db_rollback"]

_FLUSHED = "smartutils_flushed"


class MarkedAsyncSession(AsyncSession):
    async def flush(self, *args, **kwargs):
        result = await super().flush(*args, **kwargs)
        self.info[_FLUSHED] = True
        return result


class AsyncDBCli(AbstractResource):
    def __init__(self, conf: Union[MySQLConf, PostgreSQLConf], name: str):
        self._name = name
        kw = conf.kw
        kw["pool_reset_on_return"] = "rollback"
        kw["pool_pre_ping"] = True
        kw["future"] = True

        self._engine: Union[Engine, AsyncEngine] = create_async_engine(conf.url, **kw)
        self._session = sessionmaker(
            bind=self._engine,
            class_=MarkedAsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def ping(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except:  # noqa
            logger.exception("[{name}] DB ping failed", name=self._name)
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

    # async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
    #     session = self._session()
    #     try:
    #         yield session
    #     finally:
    #         await session.close()

    async def create_tables(self, bases):
        async with self.engine.begin() as conn:
            for base in bases:
                await conn.run_sync(base.metadata.create_all)


def _write_in_session(session: AsyncSession):
    written = bool(session.new) or bool(session.dirty) or bool(session.deleted)
    flushed = session.info.get(_FLUSHED, False)
    in_t = hasattr(session, "in_transaction") and session.in_transaction()
    logger.debug("written={a};flushed={b};in_t={c}", a=written, b=flushed, c=in_t)
    return written or flushed and in_t


async def db_commit(session: AsyncSession):
    # if _write_in_session(session):
    await session.commit()
    logger.debug("auto commit")


async def db_rollback(session: AsyncSession):
    # if _write_in_session(session):
    await session.rollback()
    logger.debug("auto rollback")
