import functools
import logging
import traceback
from collections.abc import AsyncGenerator
from contextvars import ContextVar
from typing import Callable, Awaitable, Any, Union, Optional

from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from smartutils.config import config

Base = declarative_base()

logger = logging.getLogger(__name__)


class DB:
    def __init__(self, key: str):
        self._name = key
        db_config = config.mysql
        self._engine: Union[Engine, AsyncEngine] = create_async_engine(db_config['url'], **db_config['engine_options'])
        self._session = sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        self._db_session_var = ContextVar(f'db_session_{self._name}')

    @property
    def engine(self):
        return self._engine

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        session = self._session()
        try:
            yield session
        finally:
            await session.close()

    def with_db(self, func: Callable[..., Awaitable[Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with self._session() as session:
                token = self._db_session_var.set(session)
                try:
                    result = await func(*args, **kwargs)
                    if session.in_transaction():
                        await session.commit()
                    return result
                except Exception as e:
                    if session.in_transaction():
                        await session.rollback()
                    logger.error(f'{self._name} with db err: {traceback.format_exc()}, will rollback')
                    raise e
                finally:
                    self._db_session_var.reset(token)

        return wrapper

    def curr_db(self) -> AsyncSession:
        try:
            return self._db_session_var.get()
        except LookupError as e:
            logger.error(f'{self._name} curr db err: {e}')
            raise RuntimeError(f'No active database session for {self._name}') from e

    async def close(self):
        await self._engine.dispose()

    async def create_tables(self, bases):
        async with self.engine.begin() as conn:
            for base in bases:
                await conn.run_sync(base.metadata.create_all)


db: Optional[DB] = None


def init(key='db'):
    global db
    db = DB(key)
