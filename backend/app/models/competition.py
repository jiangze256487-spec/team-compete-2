"""赛事模型"""
from datetime import datetime

from sqlalchemy import Integer, DateTime, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(50))
    organizer: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    banner: Mapped[str | None] = mapped_column(String(255))
    signup_start: Mapped[datetime | None] = mapped_column(DateTime)
    signup_end: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[int] = mapped_column(SmallInteger, default=0)  # 0报名中 1已结束
