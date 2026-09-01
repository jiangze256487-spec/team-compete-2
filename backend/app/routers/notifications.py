"""通知路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models import Notification, Team, TeamApplication, TeamMember, User
from ..schemas import NotificationAction, NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["通知"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    type: str = "",
    unread_only: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Notification).filter(Notification.user_id == user.id)
    if type:
        query = query.filter(Notification.type == type)
    if unread_only:
        query = query.filter(Notification.is_read == False)  # noqa: E712
    return query.order_by(Notification.created_at.desc()).all()


@router.post("/{noti_id}/read")
def mark_read(noti_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    noti = db.get(Notification, noti_id)
    if not noti or noti.user_id != user.id:
        raise HTTPException(status_code=404, detail="通知不存在")
    noti.is_read = True
    db.commit()
    return {"message": "已标记已读"}


@router.post("/{noti_id}/action", response_model=NotificationOut)
def handle_action(noti_id: int, data: NotificationAction, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """接受 / 拒绝申请或邀请"""
    noti = db.get(Notification, noti_id)
    if not noti or noti.user_id != user.id:
        raise HTTPException(status_code=404, detail="通知不存在")

    if noti.action_type == "apply":
        # 我是队长，处理入队申请
        team = db.get(Team, noti.related_id)
        if not team:
            raise HTTPException(status_code=404, detail="队伍不存在")
        applicant = db.query(TeamApplication).filter(
            TeamApplication.team_id == team.id, TeamApplication.status == "pending"
        ).order_by(TeamApplication.created_at.desc()).first()
        if data.action == "accept":
            if applicant:
                applicant.status = "approved"
                db.add(TeamMember(team_id=team.id, user_id=applicant.user_id, is_leader=False))
                team.status = "已满" if team.max_members <= len(team.members) else team.status
                db.add(Notification(
                    user_id=applicant.user_id, type="team", title="入队申请通过",
                    content=f"你已加入队伍「{team.name}」",
                ))
        elif data.action == "decline":
            if applicant:
                applicant.status = "rejected"

    elif noti.action_type == "invite":
        # 我是被邀请者，决定是否加入
        team = db.get(Team, noti.related_id)
        if not team:
            raise HTTPException(status_code=404, detail="队伍不存在")
        if data.action == "accept":
            if not db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == user.id).first():
                db.add(TeamMember(team_id=team.id, user_id=user.id, is_leader=False))
                team.status = "已满" if team.max_members <= len(team.members) else team.status
                db.add(Notification(
                    user_id=team.leader_id, type="team", title="入队成功",
                    content=f"{user.name} 已接受邀请加入队伍「{team.name}」",
                ))

    noti.is_read = True
    db.commit()
    db.refresh(noti)
    return noti
