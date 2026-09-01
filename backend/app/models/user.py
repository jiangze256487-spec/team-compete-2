"""用户模型"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    school: Mapped[str] = mapped_column(String(128), default="")
    major: Mapped[str] = mapped_column(String(128), default="")
    grade: Mapped[str] = mapped_column(String(16), default="")
    password_hash: Mapped[str] = mapped_column(String(256))
    # 技能标签 / 属性标签（JSON 数组字符串）
    skills: Mapped[str] = mapped_column(String(1024), default="[]")
    attrs: Mapped[str] = mapped_column(String(1024), default="[]")
    # 联系电话（默认隐藏，仅对方同意后展示）
    phone: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
