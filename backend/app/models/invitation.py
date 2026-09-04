"""入队邀请"""
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))    # 被邀请人
    inviter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # 邀请人
    message: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[int] = mapped_column(SmallInteger, default=0)  # 0待处理 1同意 2拒绝
    processed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
