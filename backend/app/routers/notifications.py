"""通知路由"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models import Invitation, JoinRequest, Notification, Team, TeamMember, User
from ..schemas import NotificationAction, NotificationOut
from ..serializers import serialize_notification

router = APIRouter(prefix="/api/notifications", tags=["通知"])


def _active_count(db: Session, team_id: int) -> int:
    return db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.leave_at.is_(None)
    ).count()


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    type: str = "",
    unread_only: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Notification).filter(Notification.user_id == user.id)
    if type:
        if type == "system":
            query = query.filter(Notification.type == 4)
        else:
            query = query.filter(Notification.type.in_([1, 2, 3]))
    if unread_only:
        query = query.filter(Notification.is_read == False)  # noqa: E712
    notis = query.order_by(Notification.created_at.desc()).all()
    return [serialize_notification(n) for n in notis]


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
    if not noti.related_type:
        raise HTTPException(status_code=400, detail="该通知已处理")

    if noti.related_type == "request":
        # 我是队长，处理入队申请（related_id = join_request.id）
        req = db.get(JoinRequest, noti.related_id)
        if not req or req.status != 0:
            raise HTTPException(status_code=400, detail="该申请已处理，请勿重复操作")
        team = db.get(Team, req.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="队伍不存在")
        if data.action == "accept":
            already = db.query(TeamMember).filter(
                TeamMember.team_id == team.id, TeamMember.user_id == req.user_id,
                TeamMember.leave_at.is_(None),
            ).first()
            if already:
                raise HTTPException(status_code=400, detail="对方已是队伍成员")
            req.status = 1
            req.processed_at = datetime.now()
            db.add(TeamMember(team_id=team.id, user_id=req.user_id, role=2))
            db.flush()
            if _active_count(db, team.id) >= team.max_members:
                team.status = 1
            db.add(Notification(
                user_id=req.user_id, type=3,
                content=f"你已加入队伍「{team.name}」",
                related_type="team", related_id=team.id,
            ))
        elif data.action == "decline":
            req.status = 2
            req.processed_at = datetime.now()
        else:
            raise HTTPException(status_code=400, detail="不支持的操作")

    elif noti.related_type == "invite":
        # 我是被邀请者，处理邀请（related_id = invitation.id）
        inv = db.get(Invitation, noti.related_id)
        if not inv or inv.status != 0:
            raise HTTPException(status_code=400, detail="该邀请已处理，请勿重复操作")
        team = db.get(Team, inv.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="队伍不存在")
        if data.action == "accept":
            already = db.query(TeamMember).filter(
                TeamMember.team_id == team.id, TeamMember.user_id == user.id,
                TeamMember.leave_at.is_(None),
            ).first()
            if already:
                raise HTTPException(status_code=400, detail="你已在该队伍中")
            inv.status = 1
            inv.processed_at = datetime.now()
            db.add(TeamMember(team_id=team.id, user_id=user.id, role=2))
            db.flush()
            if _active_count(db, team.id) >= team.max_members:
                team.status = 1
            db.add(Notification(
                user_id=team.captain_id, type=3,
                content=f"{user.nickname or ''} 已接受邀请加入队伍「{team.name}」",
                related_type="team", related_id=team.id,
            ))
        elif data.action == "decline":
            inv.status = 2
            inv.processed_at = datetime.now()
        else:
            raise HTTPException(status_code=400, detail="不支持的操作")
    else:
        raise HTTPException(status_code=400, detail="不支持的通知类型")

    noti.is_read = True
    noti.related_type = None  # 清除可操作标记，前端据此隐藏按钮
    db.commit()
    db.refresh(noti)
    return serialize_notification(noti)
