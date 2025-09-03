from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from pydantic import BaseModel

from smartutils.app.dao.mixin import IDMixin
from smartutils.design import MyBase
from smartutils.error.sys import LibraryUsageError
from smartutils.infra.db.base import SQLAlchemyManager
from smartutils.log import logger

try:
    from sqlalchemy import delete, update
    from sqlalchemy.engine import CursorResult
    from sqlalchemy.future import select
    from sqlalchemy.orm.attributes import InstrumentedAttribute
    from sqlalchemy.sql.elements import ColumnElement
except ImportError:
    ...

if TYPE_CHECKING:
    from sqlalchemy import delete, update
    from sqlalchemy.engine import CursorResult
    from sqlalchemy.future import select
    from sqlalchemy.orm.attributes import InstrumentedAttribute
    from sqlalchemy.sql.elements import ColumnElement

ModelType = TypeVar("ModelType", bound=IDMixin)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class DAOBase(MyBase, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    异步通用CRUD基类（SQLAlchemy 2.x/async 版本）
    - 需要db.curr为 AsyncSession 对象
    - 字段参数全部用ORM字段对象
    """

    def __init__(self, model: Type[ModelType], db: SQLAlchemyManager):
        self.model = model
        self.db = db

    @overload
    async def get(self, id: int, columns: None = None) -> Optional[ModelType]: ...
    @overload
    async def get(
        self, id: int, columns: Sequence[InstrumentedAttribute]
    ) -> Optional[Tuple[Any, ...]]: ...
    async def get(
        self, id: int, columns: Optional[Sequence[InstrumentedAttribute]] = None
    ) -> Union[Optional[ModelType], Optional[Tuple[Any, ...]]]:
        session = self.db.curr
        stmt = (select(*columns) if columns else select(self.model)).where(
            self.model.id == id
        )
        result = await session.execute(stmt)
        if columns:
            row = result.first()
            return tuple(row) if row else None  # 元组
        return result.scalar_one_or_none()  # ORM对象

    @overload
    async def get_multi(
        self,
        skip: Optional[int] = ...,
        limit: Optional[int] = ...,
        order_by: Optional[Sequence[ColumnElement]] = ...,
        last_id: Optional[int] = ...,
        columns: None = None,
    ) -> List[ModelType]: ...
    @overload
    async def get_multi(
        self,
        skip: Optional[int] = ...,
        limit: Optional[int] = ...,
        order_by: Optional[Sequence[ColumnElement]] = ...,
        last_id: Optional[int] = ...,
        columns: Sequence[InstrumentedAttribute] = ...,
    ) -> List[Tuple[Any, ...]]: ...
    async def get_multi(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[Sequence[ColumnElement]] = None,
        last_id: Optional[int] = None,
        columns: Optional[Sequence[InstrumentedAttribute]] = None,
    ) -> Union[List[ModelType], List[Tuple[Any, ...]]]:
        """
        异步方式批量获取数据，支持分页和多字段选择。

        Args:
            skip (Optional[int]): 偏移量，常用于分页，跳过前skip条记录。
            limit (Optional[int]): 查询上限，返回最多limit条。
            order_by (Optional[Sequence[ColumnElement]]): 排序字段，SQLAlchemy表达式，如 [Table.c.field1.desc()].
            last_id (Optional[int]): 基于主键(id)的游标分页，last_id大于指定值的记录。
            columns (Optional[Sequence[InstrumentedAttribute]]): 若指定，返回结构为tuple，仅包含这些字段；不指定则返回ORM对象列表。

        Returns:
            Union[List[ModelType], List[Tuple[Any, ...]]]:
                - 若columns为None，返回ModelType实例列表；
                - 若columns指定，返回字段tuple的列表。

        注意：
            skip与last_id若同时指定，只使用last_id并忽略skip。
            推荐使用last_id配合order_by主键(desc)实现高性能分页。
        """
        session = self.db.curr
        stmt = select(*columns) if columns else select(self.model)

        # 支持基于主键递增的游标分页
        if last_id is not None:
            stmt = stmt.where(self.model.id > last_id)
        if skip is not None:
            if last_id is not None:
                logger.warning("{} get_multi use last_id, ignore skip.", self.name)
            else:
                stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)
        if order_by:
            stmt = stmt.order_by(*order_by)
        result = await session.execute(stmt)

        if columns:
            return [tuple(row) for row in result.fetchall()]  # List[tuple]
        return list(result.scalars().all())  # List[ORM对象]

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        session = self.db.curr
        obj = self.model(**obj_in.model_dump())
        session.add(obj)
        await session.flush()
        return obj

    async def update(
        self,
        obj_in: UpdateSchemaType,
        filter_conditions: Sequence[ColumnElement],
        update_fields: Optional[Sequence[InstrumentedAttribute]] = None,
    ) -> int:
        """不支持orm实例更新，建议直接修改字段后commit

        Args:
            obj_in (UpdateSchemaType): 要更新的字段和值
            filter_conditions (Sequence[ColumnElement]): where条件，必需防止全表更新
            update_fields (Optional[Sequence[InstrumentedAttribute]], optional): 更新字段，可选，防止更新到意外字段. Defaults to None.

        Raises:
            LibraryUsageError: 参数使用错误

        Returns:
            int: 实际更新的行数
        """
        if not filter_conditions:
            raise LibraryUsageError(
                f"{self.name} filter_conditions cannot be empty to prevent updating the entire table!"
            )

        session = self.db.curr
        data: dict = obj_in.model_dump(exclude_unset=True)

        all_fields = set(obj_in.model_fields.keys())
        dumped_fields = set(data.keys())
        dump_removed = all_fields - dumped_fields
        if dump_removed:
            logger.info("{} filtered out by unset: {}", self.name, dump_removed)

        if update_fields:
            allowed_names = {attr.key for attr in update_fields}
            fields_removed = set(data.keys()) - allowed_names
            if fields_removed:
                logger.error("{} filtered out by fields: {}", self.name, fields_removed)
            data = {k: v for k, v in data.items() if k in allowed_names}
        stmt = update(self.model).where(*filter_conditions).values(**data)
        result = await session.execute(stmt)
        return cast(CursorResult, result).rowcount or 0

    async def remove(self, filter_conditions: Sequence[ColumnElement]) -> int:
        if not filter_conditions:
            raise LibraryUsageError(
                f"{self.name} filter_conditions cannot be empty to prevent deleting the entire table!"
            )
        session = self.db.curr
        stmt = delete(self.model).where(*filter_conditions)
        result = await session.execute(stmt)
        return cast(CursorResult, result).rowcount or 0
