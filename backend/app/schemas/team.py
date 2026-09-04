"""队伍相关序列化模型"""
from datetime import datetime

from pydantic import BaseModel


class MemberBrief(BaseModel):
    user_id: int
    name: str
    school: str = ""
    grade: str = ""
    skills: list[str] = []
    is_leader: bool = False


class TeamOut(BaseModel):
    id: int
    name: str
    leader_id: int
    leader_name: str = ""
    event_name: str = ""
    school: str = ""
    desc: str = ""
    status: str = "招募中"
    max_members: int = 4
    tags: list[str] = []
    members_count: int = 0
    created_at: datetime | None = None  # 新表无 created_at，用队长入队时间近似


class TeamDetail(TeamOut):
    members: list[MemberBrief] = []
    my_application_status: str = ""


class TeamCreate(BaseModel):
    name: str
    event_name: str = ""  # 前端传赛事名，后端映射到 competition_id
    desc: str = ""
    max_members: int = 4
    tags: list[str] = []


class TeamUpdate(BaseModel):
    name: str | None = None
    event_name: str | None = None
    desc: str | None = None
    status: str | None = None
    max_members: int | None = None
    tags: list[str] | None = None


class ApplyResult(BaseModel):
    message: str
    applied: bool = True
