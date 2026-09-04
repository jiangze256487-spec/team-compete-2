"""通知模型"""
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    type: Mapped[int] = mapped_column(SmallInteger)  # 1入队申请 2入队邀请 3离队通知 4系统通知
    content: Mapped[str] = mapped_column(String(500))
    related_type: Mapped[str | None] = mapped_column(String(30))  # team/request/invite
    related_id: Mapped[int | None] = mapped_column(BigInteger)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
