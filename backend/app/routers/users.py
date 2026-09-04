"""用户路由：个人资料与标签"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, get_optional_user
from ..database import get_db
from ..models import TeamMember, User
from ..schemas import UserOut, UserTagsUpdate, UserUpdate
from ..serializers import serialize_user, set_user_tags

router = APIRouter(prefix="/api/users", tags=["用户"])

# 对外字段名 -> 模型字段名
_UPDATE_FIELDS = {"name": "nickname", "school": "school", "major": "major", "grade": "grade", "phone": "phone"}


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return serialize_user(db, user)


@router.put("/me", response_model=UserOut)
def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for api_field, model_field in _UPDATE_FIELDS.items():
        value = getattr(data, api_field)
        if value is not None:
            setattr(user, model_field, value)
    db.commit()
    db.refresh(user)
    return serialize_user(db, user)


@router.put("/me/tags", response_model=UserOut)
def update_tags(data: UserTagsUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    set_user_tags(db, user.id, data.skills, data.attrs)
    db.commit()
    db.refresh(user)
    return serialize_user(db, user)


def _shares_team(db: Session, a: int, b: int) -> bool:
    """判断两个用户是否同属至少一个队伍（即已成为队友）"""
    teams_a = {m.team_id for m in db.query(TeamMember).filter(TeamMember.user_id == a).all()}
    if not teams_a:
        return False
    return db.query(TeamMember).filter(
        TeamMember.user_id == b, TeamMember.team_id.in_(teams_a)
    ).first() is not None


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), viewer: User | None = Depends(get_optional_user)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    out = serialize_user(db, target)
    # 联系方式隐私：仅本人或同队成员可见电话
    can_view_phone = viewer is not None and (viewer.id == target.id or _shares_team(db, viewer.id, target.id))
    if not can_view_phone:
        out.phone = ""
    return out
