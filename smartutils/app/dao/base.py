from __future__ import annotations

from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
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
    from sqlalchemy import Select, delete, update
    from sqlalchemy.engine import CursorResult
    from sqlalchemy.future import select
    from sqlalchemy.orm import DeclarativeMeta
    from sqlalchemy.orm.attributes import InstrumentedAttribute
    from sqlalchemy.sql.elements import ColumnElement
except ImportError:
    ...

if TYPE_CHECKING:
    from sqlalchemy import Select, delete, update
    from sqlalchemy.engine import CursorResult
    from sqlalchemy.future import select
    from sqlalchemy.orm import DeclarativeMeta
    from sqlalchemy.orm.attributes import InstrumentedAttribute
    from sqlalchemy.sql.elements import ColumnElement


ModelType = TypeVar("ModelType", bound=IDMixin)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class ColumnsType(int, Enum):
    MODEL = 1
    TUPLE = 2
    VALUE = 3


class DAOBase(MyBase, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    异步通用CRUD基类（SQLAlchemy 2.x/async 版本）
    - 需要db.curr为 AsyncSession 对象
    - 字段参数全部用ORM字段对象
    """

    def __init__(self, model: Type[ModelType], db: SQLAlchemyManager):
        self.model = model
        self.db = db

    def _columns_type(
        self,
        columns: Union[None, InstrumentedAttribute, Sequence[InstrumentedAttribute]],
    ) -> ColumnsType:
        if columns is None:
            return ColumnsType.MODEL
        if isinstance(columns, InstrumentedAttribute):
            return ColumnsType.VALUE
        if isinstance(columns, Sequence) and not isinstance(columns, str):
            # 如果columns只包含一个元素，按单VALUE算
            return ColumnsType.VALUE if len(columns) == 1 else ColumnsType.TUPLE

        raise LibraryUsageError(f"columns {columns} invalid!")

    def _build_select_stmt(self, columns) -> Tuple[ColumnsType, Select]:
        columns_type = self._columns_type(columns)
        if columns_type == ColumnsType.MODEL:
            return columns_type, select(self.model)
        if columns_type == ColumnsType.TUPLE:
            return columns_type, select(*columns)
        # 单字段
        # if columns_type == ColumnsType.VALUE:
        if isinstance(columns, InstrumentedAttribute):
            return columns_type, select(columns)
        else:
            return columns_type, select(columns[0])

    @overload
    async def get(
        self,
        columns: None = None,
        id: Optional[int] = None,
        filter_conditions: Optional[Sequence[ColumnElement]] = None,
        order_by: Optional[Sequence[ColumnElement]] = None,
    ) -> Optional[ModelType]: ...
    @overload
    async def get(
        self,
        columns: InstrumentedAttribute = ...,
        id: Optional[int] = None,
        filter_conditions: Optional[Sequence[ColumnElement]] = None,
        order_by: Optional[Sequence[ColumnElement]] = None,
    ) -> Optional[Any]: ...
    @overload
    async def get(
        self,
        columns: Sequence[InstrumentedAttribute],
        id: Optional[int] = None,
        filter_conditions: Optional[Sequence[ColumnElement]] = None,
        order_by: Optional[Sequence[ColumnElement]] = None,
    ) -> Union[None, Tuple[Any, ...], Any]: ...
    async def get(
        self,
        columns: Union[
            None, InstrumentedAttribute, Sequence[InstrumentedAttribute]
        ] = None,
        id: Optional[int] = None,
        filter_conditions: Optional[Sequence[ColumnElement]] = None,
        order_by: Optional[Sequence[ColumnElement]] = None,
    ) -> Union[None, ModelType, Tuple[Any, ...], Any]:
        """
        获取单条数据，支持主键或自定义条件查询，并灵活指定返回字段。

        参数:
        columns:
        - None：返回 ORM 实体对象。
        - InstrumentedAttribute（如 User.id）：返回该字段值。
        - Sequence[InstrumentedAttribute]：返回指定字段元组，若只传一个字段则退化为单值。
        id:
        主键id，优先以此作为查询条件。
        filter_conditions:
        过滤条件，id为None时生效，可指定任意SQLAlchemy表达式列表。

        返回:
        - columns为None：返回单个 ORM 实例或 None
        - columns为单字段：直接返回该字段的值或 None
        - columns为多字段：返回字段元组或 None

        用法说明:
        - 优先通过id查找，id为空时尝试用filter_conditions
        - 同时传id和filter_conditions时，仅使用id - 查询无匹配时返回None
        """
        session = self.db.curr
        columns_type, stmt = self._build_select_stmt(columns)

        # 优先用id作为查询条件
        if id is not None:
            stmt = stmt.where(self.model.id == id)
        elif filter_conditions:
            stmt = stmt.where(*filter_conditions)
        if order_by:
            stmt = stmt.order_by(*order_by)
        result = await session.execute(stmt)

        # 获取返回结果
        row = result.first()
        if columns_type in (ColumnsType.MODEL, ColumnsType.VALUE):
            return row[0] if row else None  # scalar_one_or_none兼容写法
        # if columns_type == ColumnsType.TUPLE:
        return tuple(row) if row else None

    @overload
    async def get_multi(
        self,
        columns: None = None,
        filter_conditions: Sequence[ColumnElement] = ...,
        skip: Optional[int] = ...,
        limit: Optional[int] = ...,
        order_by: Optional[Sequence[ColumnElement]] = ...,
        last_id: Optional[int] = ...,
    ) -> Sequence[ModelType]: ...
    @overload
    async def get_multi(
        self,
        columns: InstrumentedAttribute = ...,
        filter_conditions: Sequence[ColumnElement] = ...,
        skip: Optional[int] = ...,
        limit: Optional[int] = ...,
        order_by: Optional[Sequence[ColumnElement]] = ...,
        last_id: Optional[int] = ...,
    ) -> Sequence[Any]: ...
    @overload
    async def get_multi(
        self,
        columns: Sequence[InstrumentedAttribute] = ...,
        filter_conditions: Sequence[ColumnElement] = ...,
        skip: Optional[int] = ...,
        limit: Optional[int] = ...,
        order_by: Optional[Sequence[ColumnElement]] = ...,
        last_id: Optional[int] = ...,
    ) -> Union[Sequence[Tuple[Any, ...]], Sequence[Any]]: ...
    async def get_multi(
        self,
        columns: Union[
            None, Sequence[InstrumentedAttribute], InstrumentedAttribute
        ] = None,
        filter_conditions: Sequence[ColumnElement] = (),
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[Sequence[ColumnElement]] = None,
        last_id: Optional[int] = None,
    ) -> Union[Sequence[ModelType], Sequence[Any], Sequence[Tuple[Any, ...]]]:
        """
        批量获取数据，支持条件过滤、字段选择和多样化分页方式。

        参数:
        columns:
        - None：返回 ORM 实体对象的序列。
        - InstrumentedAttribute（如 User.id）：返回单字段值的序列。
        - Sequence[InstrumentedAttribute]：返回元组（多字段）或单值（单字段）序列。
        filter_conditions:
        过滤条件，可为任意SQLAlchemy表达式组成的序列。
        skip:
        跳过前N项，常用于偏移式分页，若last_id非空则无效。
        limit:
        最大条数限制。
        order_by:
        排序条件，支持多条件排序。
        last_id:
        游标式分页主键，仅返回主键大于last_id的数据；优先于skip。

        返回:
        - columns为None：返回 ORM 实体对象序列
        - columns为单字段：返回该字段值的序列
        - columns为多字段：返回字段元组或（单字段时）值的序列

        用法说明:
        - 支持自定义where、limit、offset、order_by
        - 推荐 last_id + order_by 配合主键分页以提升性能
        - relation字段建议用序列方式传入以获得最佳类型支持
        """
        session = self.db.curr
        columns_type = self._columns_type(columns)
        columns_type, stmt = self._build_select_stmt(columns)

        if filter_conditions:
            stmt = stmt.where(*filter_conditions)
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

        # 获取返回结果
        if columns_type == ColumnsType.MODEL:
            return result.scalars().all()

        rows = result.fetchall()
        if columns_type == ColumnsType.TUPLE:
            return [tuple(row) for row in rows]
        return [row[0] for row in rows]

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        session = self.db.curr
        obj = self.model(**obj_in.model_dump(exclude_unset=True))
        session.add(obj)
        await session.flush()
        return obj

    async def update(
        self,
        obj_in: UpdateSchemaType,
        filter_conditions: Sequence[ColumnElement],
        update_fields: Optional[Sequence[InstrumentedAttribute]] = None,
        create_on_none: bool = False,
        trans_create_schema=lambda x: x,
        exclude_none: bool = True,
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

        if create_on_none:
            exist = await self.get(
                columns=[self.model.id], filter_conditions=filter_conditions
            )
            if not exist:
                logger.info("update auto use update schema to create.")
                await self.create(trans_create_schema(obj_in))
                return 1

        session = self.db.curr
        data: dict = obj_in.model_dump(exclude_unset=True, exclude_none=exclude_none)
        if not data:
            logger.info(
                "{} update by {} empty, do nothing.", self.name, filter_conditions
            )
            return 0

        dump_removed = set(obj_in.model_fields.keys()) - set(data.keys())
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


class CommentMeta(DeclarativeMeta):
    def __init__(cls, name, bases, dict_):
        super().__init__(name, bases, dict_)
        pydantic_cls: Optional[Type[BaseModel]] = getattr(cls, "__pydantic__", None)
        if not pydantic_cls:
            return

        desc_map = {
            k: v.description
            for k, v in pydantic_cls.model_fields.items()
            if v.description
        }
        for col in cls.__table__.columns:  # type: ignore
            if not col.comment and col.name in desc_map:
                col.comment = desc_map[col.name]
