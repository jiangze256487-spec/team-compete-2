"""标签模型"""
from sqlalchemy import BigInteger, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    type: Mapped[int] = mapped_column(SmallInteger)  # 1技能 2角色 3其他


class UserTag(Base):
    __tablename__ = "user_tags"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tags.id"), primary_key=True)


class TeamTag(Base):
    __tablename__ = "team_tags"

    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tags.id"), primary_key=True)
