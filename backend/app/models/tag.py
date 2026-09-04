"""标签模型"""
from sqlalchemy import ForeignKey, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Tag(Base):
    """全局标签：同一名称可存在于不同语境（技能/角色/队伍），按 (name, type) 区分"""
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("name", "type", name="uq_tag_name_type"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    type: Mapped[int] = mapped_column(SmallInteger)  # 1技能 2角色 3其他


class UserTag(Base):
    __tablename__ = "user_tags"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), primary_key=True)


class TeamTag(Base):
    __tablename__ = "team_tags"

    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), primary_key=True)
