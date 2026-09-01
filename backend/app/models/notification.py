"""通知模型"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    type: Mapped[str] = mapped_column(String(16), default="team")  # team / event / system
    title: Mapped[str] = mapped_column(String(128))
    content: Mapped[str] = mapped_column(String(512), default="")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    # 可操作类型：apply / invite，对应业务关联 ID
    action_type: Mapped[str] = mapped_column(String(16), default="")
    related_id: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
