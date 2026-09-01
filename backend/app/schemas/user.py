"""用户相关序列化模型"""
import json
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    student_id: str
    name: str
    school: str = ""
    major: str = ""
    grade: str = ""


class UserRegister(UserBase):
    password: str = Field(min_length=6, max_length=64)


class UserLogin(BaseModel):
    student_id: str
    password: str


class UserOut(UserBase):
    id: int
    skills: list[str] = []
    attrs: list[str] = []
    phone: str = ""
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("skills", "attrs", mode="before")
    @classmethod
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v or "[]")
            except json.JSONDecodeError:
                return []
        return v or []


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
