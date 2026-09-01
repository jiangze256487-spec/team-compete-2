"""赛事相关序列化模型"""
from datetime import datetime

from pydantic import BaseModel


class EventOut(BaseModel):
    id: int
    name: str
    category: str
    org: str = ""
    desc: str = ""
    deadline: str = ""

    model_config = {"from_attributes": True}


class EventCreate(BaseModel):
    name: str
    category: str
    org: str = ""
    desc: str = ""
    deadline: str = ""


class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
