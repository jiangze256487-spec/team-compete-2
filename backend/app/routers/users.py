"""用户路由：个人资料与标签"""
import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import UserOut, UserTagsUpdate, UserUpdate

router = APIRouter(prefix="/api/users", tags=["用户"])


def _load_json(raw: str) -> list[str]:
    try:
        return json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserOut)
def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for field in ["name", "school", "major", "grade", "phone"]:
        value = getattr(data, field)
        if value is not None:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.put("/me/tags", response_model=UserOut)
def update_tags(data: UserTagsUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.skills = json.dumps(data.skills, ensure_ascii=False)
    user.attrs = json.dumps(data.attrs, ensure_ascii=False)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
