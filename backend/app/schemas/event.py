"""赛事相关序列化模型（对外字段保持前端兼容）"""
from pydantic import BaseModel


class EventOut(BaseModel):
    id: int
    name: str
    category: str = ""
    org: str = ""
    desc: str = ""
    deadline: str = ""
    teams_count: int = 0


class EventCreate(BaseModel):
    name: str
    category: str = ""
    org: str = ""
    desc: str = ""
    deadline: str = ""


class CategoryOut(BaseModel):
    id: int
    name: str
