"""队伍模型"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    competition_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("competitions.id"))
    captain_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    description: Mapped[str | None] = mapped_column(Text)
    max_members: Mapped[int] = mapped_column(Integer, default=4)
    status: Mapped[int] = mapped_column(SmallInteger, default=0)  # 0招募中 1已满员 2已解散

    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    role: Mapped[int] = mapped_column(SmallInteger)  # 1队长 2队员
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    leave_at: Mapped[datetime | None] = mapped_column(DateTime)  # NULL 代表在队

    team = relationship("Team", back_populates="members")


class JoinRequest(Base):
    """入队申请"""
    __tablename__ = "join_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    message: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[int] = mapped_column(SmallInteger, default=0)  # 0待处理 1同意 2拒绝
    processed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
