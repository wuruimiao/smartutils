# tests/app/test_dao_comment.py

from pydantic import BaseModel, Field
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from smartutils.app.dao.base import CommentMeta


# 1. 定义pydantic模型，带description
class UserSchema(BaseModel):
    id: int = Field(description="用户ID描述")
    name: str = Field(description="用户名描述")


# 2. 声明SQLAlchemy ORM模型（用CommentMeta）
Base = declarative_base(metaclass=CommentMeta)


class User(Base):
    __tablename__ = "test_user"
    __pydantic__ = UserSchema

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment=None)
    name: Mapped[str] = mapped_column(String(50), comment=None)


def test_commentmeta_syncs_description_to_comment():
    # 检查column.comment是否被补全
    assert User.__table__.columns["id"].comment == "用户ID描述"
    assert User.__table__.columns["name"].comment == "用户名描述"


def test_commentmeta_does_not_override_existing_comment():
    class MySchema(BaseModel):
        col1: int = Field(description="schema desc")

    Base2 = declarative_base(metaclass=CommentMeta)

    class MyTable(Base2):
        __tablename__ = "t2"
        __pydantic__ = MySchema
        col1: Mapped[int] = mapped_column(Integer, primary_key=True, comment="已有注释")

    # 已有comment的不被覆盖
    assert MyTable.__table__.columns["col1"].comment == "已有注释"


def test_commentmeta_no_pydantic():
    # 没有__pydantic__属性，应该不会报错也无操作
    Base3 = declarative_base(metaclass=CommentMeta)

    class SimpleTable(Base3):
        __tablename__ = "t3"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # 应该正常生成，comment为None
    assert SimpleTable.__table__.columns["id"].comment is None
