import sys
from typing import TYPE_CHECKING

from smartutils.infra.db.sqlalchemy_cli import AsyncDBCli
from smartutils.infra.resource.manager.manager import CTXResourceManager
from smartutils.init.mixin import LibraryCheckMixin

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override

try:
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyManager(LibraryCheckMixin, CTXResourceManager[AsyncDBCli]):
    # 屏蔽校验：DB返回值不是资源实例本身
    @property
    @override
    def curr(self) -> AsyncSession:  # pyright: ignore[reportIncompatibleMethodOverride]
        return super().curr[0]  # pyright: ignore[reportIndexIssue]
