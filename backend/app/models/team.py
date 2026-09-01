"""队伍模型"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    leader_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_name: Mapped[str] = mapped_column(String(64), default="")
    school: Mapped[str] = mapped_column(String(128), default="")
    desc: Mapped[str] = mapped_column(String(2000), default="")
    status: Mapped[str] = mapped_column(String(16), default="招募中")  # 招募中 / 已满 / 已结束
    max_members: Mapped[int] = mapped_column(Integer, default=4)
    tags: Mapped[str] = mapped_column(String(1024), default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_leader: Mapped[bool] = mapped_column(default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    team = relationship("Team", back_populates="members")


class TeamApplication(Base):
    """入队申请"""
    __tablename__ = "team_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending / approved / rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
