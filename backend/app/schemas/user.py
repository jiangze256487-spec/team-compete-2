"""用户相关序列化模型"""
from datetime import datetime

from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    student_id: str  # 对应表 student_no
    name: str        # 对应表 nickname
    school: str = ""
    major: str = ""
    grade: str = ""


class UserRegister(UserBase):
    phone: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=6, max_length=64)


class UserLogin(BaseModel):
    student_id: str
    password: str


class UserOut(BaseModel):
    id: int
    student_id: str
    name: str
    school: str = ""
    major: str = ""
    grade: str = ""
    skills: list[str] = []
    attrs: list[str] = []
    phone: str = ""
    created_at: datetime


class UserUpdate(BaseModel):
    name: str | None = None
    school: str | None = None
    major: str | None = None
    grade: str | None = None
    phone: str | None = None


class UserTagsUpdate(BaseModel):
    skills: list[str] = []
    attrs: list[str] = []


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
