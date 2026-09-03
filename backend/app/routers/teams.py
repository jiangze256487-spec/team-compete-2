"""队伍路由：列表 / 创建 / 详情 / 申请 / 邀请"""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models import Notification, Team, TeamApplication, TeamMember, User
from ..schemas import ApplyResult, MemberBrief, TeamCreate, TeamDetail, TeamOut, TeamUpdate

router = APIRouter(prefix="/api/teams", tags=["队伍"])


def _load_json(raw: str) -> list[str]:
    try:
        return json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []


def _serialize_team(db: Session, team: Team) -> dict:
    members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()
    leader = db.get(User, team.leader_id)
    return {
        "id": team.id,
        "name": team.name,
        "leader_id": team.leader_id,
        "leader_name": leader.name if leader else "",
        "event_name": team.event_name,
        "school": team.school,
        "desc": team.desc,
        "status": team.status,
        "max_members": team.max_members,
        "tags": _load_json(team.tags),
        "members_count": len(members),
        "created_at": team.created_at,
    }


def _serialize_detail(db: Session, team: Team) -> dict:
    data = _serialize_team(db, team)
    members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()
    briefs = []
    for m in members:
        u = db.get(User, m.user_id)
        if not u:
            continue
        briefs.append(MemberBrief(
            user_id=u.id, name=u.name, school=u.school, grade=u.grade,
            skills=_load_json(u.skills), is_leader=m.is_leader,
        ))
    data["members"] = briefs
    return data


@router.get("", response_model=list[TeamOut])
def list_teams(
    search: str = "",
    event: str = "",
    skill: str = "",
    grade: str = "",
    db: Session = Depends(get_db),
):
    teams = db.query(Team).order_by(Team.created_at.desc()).all()
    result = []
    for t in teams:
        data = _serialize_team(db, t)
        if search and search not in t.name and search not in t.desc:
            continue
        if event and t.event_name != event:
            continue
        if skill and skill not in _load_json(t.tags):
            continue
        if grade:
            members = db.query(TeamMember).filter(TeamMember.team_id == t.id).all()
            user_ids = [m.user_id for m in members]
            if user_ids:
                has_grade = db.query(User).filter(User.id.in_(user_ids), User.grade == grade).first()
                if not has_grade:
                    continue
        result.append(data)
    return result


@router.post("", response_model=TeamDetail, status_code=201)
def create_team(data: TeamCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = Team(
        name=data.name,
        leader_id=user.id,
        event_name=data.event_name,
        school=user.school,
        desc=data.desc,
        max_members=max(data.max_members, 2),
        tags=json.dumps(data.tags, ensure_ascii=False),
    )
    db.add(team)
    db.flush()
    db.add(TeamMember(team_id=team.id, user_id=user.id, is_leader=True))
    db.commit()
    db.refresh(team)
    return _serialize_detail(db, team)


@router.get("/{team_id}", response_model=TeamDetail)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    return _serialize_detail(db, team)


@router.patch("/{team_id}", response_model=TeamDetail)
def update_team(team_id: int, data: TeamUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    if team.leader_id != user.id:
        raise HTTPException(status_code=403, detail="仅队长可修改队伍")
    for field in ["name", "event_name", "desc", "status", "max_members"]:
        value = getattr(data, field)
        if value is not None:
            setattr(team, field, value)
    if data.tags is not None:
        team.tags = json.dumps(data.tags, ensure_ascii=False)
    db.commit()
    db.refresh(team)
    return _serialize_detail(db, team)


@router.delete("/{team_id}")
def delete_team(team_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    if team.leader_id != user.id:
        raise HTTPException(status_code=403, detail="仅队长可解散队伍")
    db.delete(team)
    db.commit()
    return {"message": "队伍已解散"}


@router.post("/{team_id}/apply", response_model=ApplyResult)
def apply_team(team_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    # 已在队内
    if db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user.id).first():
        raise HTTPException(status_code=400, detail="你已是该队伍成员")
    # 已有待处理申请
    if db.query(TeamApplication).filter(
        TeamApplication.team_id == team_id,
        TeamApplication.user_id == user.id,
        TeamApplication.status == "pending",
    ).first():
        raise HTTPException(status_code=400, detail="你已申请过该队伍，等待审核中")
    db.add(TeamApplication(team_id=team_id, user_id=user.id, status="pending"))
    # 给队长发通知
    db.add(Notification(
        user_id=team.leader_id, type="team", title="申请入队提醒",
        content=f"{user.name} 申请加入你的队伍「{team.name}」",
        action_type="apply", related_id=team.id,
    ))
    db.commit()
    return ApplyResult(message="申请已提交，等待队长审核")


@router.post("/{team_id}/invite", response_model=ApplyResult)
def invite_user(team_id: int, invitee_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """队长邀请指定学号用户入队"""
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")
    if team.leader_id != user.id:
        raise HTTPException(status_code=403, detail="仅队长可邀请成员")
    invitee = db.get(User, invitee_id)
    if not invitee:
        raise HTTPException(status_code=404, detail="用户不存在")
    if db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == invitee_id).first():
        raise HTTPException(status_code=400, detail="对方已是该队伍成员")
    db.add(Notification(
        user_id=invitee_id, type="team", title="被邀请入队提醒",
        content=f"{user.name} 邀请你加入队伍「{team.name}」",
        action_type="invite", related_id=team.id,
    ))
    db.commit()
    return ApplyResult(message="邀请已发送")


@router.post("/{team_id}/leave")
def leave_team(team_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user.id).first()
    if not member:
        raise HTTPException(status_code=400, detail="你不在该队伍中")
    team = db.get(Team, team_id)
    if member.is_leader:
        raise HTTPException(status_code=400, detail="队长请先转让或解散队伍")
    db.delete(member)
    # 给队长发离队提醒
    if team:
        db.add(Notification(
            user_id=team.leader_id, type="team", title="队友离队提醒",
            content=f"{user.name} 已退出队伍「{team.name}」",
        ))
    db.commit()
    return {"message": "已退出队伍"}
