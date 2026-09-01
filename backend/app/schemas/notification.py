"""通知相关序列化模型"""
from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    content: str = ""
    is_read: bool = False
    action_type: str = ""
    related_id: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationAction(BaseModel):
    """接受/拒绝通知动作"""
    action: str  # accept / decline
