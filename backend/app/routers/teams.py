"""队伍路由：列表 / 创建 / 详情 / 申请 / 邀请（新 schema：competitions / captain_id / join_requests）"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, get_optional_user
from ..database import get_db
from ..models import Competition, Invitation, JoinRequest, Notification, Team, TeamMember, User
from ..schemas import ApplyResult, TeamCreate, TeamDetail, TeamOut, TeamUpdate
from ..serializers import (
    TEAM_STATUS_REVERSE,
    serialize_team,
    serialize_team_members,
    set_team_tags,
)

router = APIRouter(prefix="/api/teams", tags=["队伍"])


# ===== 内部辅助 =====

def _active_members(db: Session, team_id: int) -> list[TeamMember]:
    return db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.leave_at.is_(None)
    ).all()


def _active_member_count(db: Session, team_id: int) -> int:
    return db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.leave_at.is_(None)
    ).count()


def _find_competition(db: Session, name: str) -> Competition | None:
    if not name:
        return None
    return db.query(Competition).filter(Competition.name == name).first()


def _reopen_if_not_full(db: Session, team: Team) -> None:
    """满员队伍在有人离开后恢复为招募中"""
    if team.status == 1 and _active_member_count(db, team.id) < team.max_members:
        team.status = 0


def _detail(db: Session, team: Team, viewer_id: int | None = None) -> dict:
    """队伍详情（对外兼容字段：leader_id/event_name/... + members + 我的申请状态）"""
    data = serialize_team(db, team)
    data["members"] = serialize_team_members(db, team.id)
    data["my_application_status"] = ""
    if viewer_id is not None:
        pending = db.query(JoinRequest).filter(
            JoinRequest.team_id == team.id,
            JoinRequest.user_id == viewer_id,
            JoinRequest.status == 0,
        ).first()
        data["my_application_status"] = "pending" if pending else ""
    return data


# ===== 接口 =====

@router.get("", response_model=list[TeamOut])
def list_teams(
    search: str = "",
    event: str = "",
    skill: str = "",
    grade: str = "",
    db: Session = Depends(get_db),
):
    teams = db.query(Team).order_by(Team.id.desc()).all()
    result = []
    for t in teams:
        data = serialize_team(db, t)
        if search:
            haystack = f"{t.name} {t.description or ''} {data['event_name']} {' '.join(data['tags'])}"
            if search not in haystack:
                continue
        if event and data["event_name"] != event:
            continue
        if skill and skill not in data["tags"]:
            continue
        if grade:
            user_ids = [m.user_id for m in _active_members(db, t.id)]
            if user_ids:
                has_grade = db.query(User).filter(User.id.in_(user_ids), User.grade == grade).first()
                if not has_grade:
                    continue
        result.append(data)
    return result


@router.post("", response_model=TeamDetail, status_code=201)
def create_team(data: TeamCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    comp = _find_competition(db, data.event_name)
    if not comp:
        raise HTTPException(status_code=400, detail="未找到对应赛事，请先创建赛事")
    team = Team(
        name=data.name,
        competition_id=comp.id,
        captain_id=user.id,
        description=data.desc or None,
        max_members=max(data.max_members, 2),
        status=0,
    )
    db.add(team)
    db.flush()
    db.add(TeamMember(team_id=team.id, user_id=user.id, role=1))
    set_team_tags(db, team.id, data.tags)
    db.commit()
    db.refresh(team)
    return _detail(db, team, viewer_id=user.id)


@router.get("/{team_id}", response_model=TeamDetail)
def get_team(team_id: int, user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    return _detail(db, team, viewer_id=user.id if user else None)


@router.patch("/{team_id}", response_model=TeamDetail)
def update_team(team_id: int, data: TeamUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    if team.captain_id != user.id:
        raise HTTPException(status_code=403, detail="仅队长可修改队伍")
    if data.name is not None:
        team.name = data.name
    if data.desc is not None:
        team.description = data.desc or None
    if data.max_members is not None:
        team.max_members = max(data.max_members, 2)
    if data.event_name:
        comp = _find_competition(db, data.event_name)
        if not comp:
            raise HTTPException(status_code=400, detail="未找到对应赛事")
        team.competition_id = comp.id
    if data.status is not None:
        team.status = TEAM_STATUS_REVERSE.get(data.status, team.status)
    if data.tags is not None:
        set_team_tags(db, team.id, data.tags)
    db.commit()
    db.refresh(team)
    return _detail(db, team, viewer_id=user.id)


@router.delete("/{team_id}")
def delete_team(team_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    if team.captain_id != user.id:
        raise HTTPException(status_code=403, detail="仅队长可解散队伍")
    db.delete(team)
    db.commit()
    return {"message": "队伍已解散"}


@router.post("/{team_id}/apply", response_model=ApplyResult)
def apply_team(team_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    if team.status == 2:
        raise HTTPException(status_code=400, detail="队伍已解散")
    # 已在队内
    if db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == user.id, TeamMember.leave_at.is_(None)
    ).first():
        raise HTTPException(status_code=400, detail="你已是该队伍成员")
    # 已有待处理申请
    if db.query(JoinRequest).filter(
        JoinRequest.team_id == team_id, JoinRequest.user_id == user.id, JoinRequest.status == 0
    ).first():
        raise HTTPException(status_code=400, detail="你已申请过该队伍，等待审核中")
    req = JoinRequest(team_id=team_id, user_id=user.id, status=0)
    db.add(req)
    db.flush()
    db.add(Notification(
        user_id=team.captain_id, type=1,
        content=f"{user.nickname or ''} 申请加入你的队伍「{team.name}」",
        related_type="request", related_id=req.id,
    ))
    db.commit()
    return ApplyResult(message="申请已提交，等待队长审核")


@router.post("/{team_id}/invite", response_model=ApplyResult)
def invite_user(team_id: int, invitee_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """队长邀请指定用户入队"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    if team.status == 2:
        raise HTTPException(status_code=400, detail="队伍已解散")
    if team.captain_id != user.id:
        raise HTTPException(status_code=403, detail="仅队长可邀请成员")
    invitee = db.get(User, invitee_id)
    if not invitee:
        raise HTTPException(status_code=404, detail="用户不存在")
    if db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == invitee_id, TeamMember.leave_at.is_(None)
    ).first():
        raise HTTPException(status_code=400, detail="对方已是该队伍成员")
    inv = Invitation(team_id=team_id, user_id=invitee_id, inviter_id=user.id, status=0)
    db.add(inv)
    db.flush()
    db.add(Notification(
        user_id=invitee_id, type=2,
        content=f"{user.nickname or ''} 邀请你加入队伍「{team.name}」",
        related_type="invite", related_id=inv.id,
    ))
    db.commit()
    return ApplyResult(message="邀请已发送")


@router.post("/{team_id}/leave")
def leave_team(team_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == user.id, TeamMember.leave_at.is_(None)
    ).first()
    if not member:
        raise HTTPException(status_code=400, detail="你不在该队伍中")
    team = db.get(Team, team_id)
    if member.role == 1:
        raise HTTPException(status_code=400, detail="队长请先转让或解散队伍")
    member.leave_at = datetime.now()
    _reopen_if_not_full(db, team)
    db.add(Notification(
        user_id=team.captain_id, type=3,
        content=f"{user.nickname or ''} 已退出队伍「{team.name}」",
        related_type="team", related_id=team.id,
    ))
    db.commit()
    return {"message": "已退出队伍"}


@router.post("/{team_id}/members/{user_id}/remove")
def remove_member(team_id: int, user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """队长移除指定成员"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    if team.captain_id != user.id:
        raise HTTPException(status_code=403, detail="仅队长可移除成员")
    if user_id == team.captain_id:
        raise HTTPException(status_code=400, detail="不能移除队长本人")
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == user_id, TeamMember.leave_at.is_(None)
    ).first()
    if not member:
        raise HTTPException(status_code=400, detail="对方不在该队伍中")
    removed_user = db.get(User, user_id)
    member.leave_at = datetime.now()
    _reopen_if_not_full(db, team)
    db.add(Notification(
        user_id=user_id, type=3,
        content=f"你已被移出队伍「{team.name}」",
        related_type="team", related_id=team.id,
    ))
    db.commit()
    return {"message": f"已移除成员{removed_user.nickname or ''}"}
