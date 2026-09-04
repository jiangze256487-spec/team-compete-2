"""序列化辅助：把新表模型映射为前端兼容的 schema 对象"""
from sqlalchemy.orm import Session

from .models import (
    Competition, Notification, Tag, Team, TeamMember, TeamTag, User, UserTag,
)

# 标签类型
TAG_SKILL = 1
TAG_ROLE = 2
TAG_OTHER = 3

# 队伍状态：数字 -> 前端字符串
TEAM_STATUS_MAP = {0: "招募中", 1: "已满员", 2: "已解散"}
TEAM_STATUS_REVERSE = {"招募中": 0, "已满员": 1, "已解散": 2}

# 通知类型：数字 -> 前端字符串
NOTI_TYPE_MAP = {1: "team", 2: "team", 3: "team", 4: "system"}
NOTI_TITLE_MAP = {1: "入队申请", 2: "入队邀请", 3: "离队通知", 4: "系统通知"}


def get_or_create_tag(db: Session, name: str, tag_type: int) -> Tag:
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        tag = Tag(name=name, type=tag_type)
        db.add(tag)
        db.flush()
    return tag


def get_user_tags(db: Session, user_id: int) -> tuple[list[str], list[str]]:
    """返回 (skills, attrs)"""
    rows = (
        db.query(Tag.name, Tag.type)
        .join(UserTag, UserTag.tag_id == Tag.id)
        .filter(UserTag.user_id == user_id)
        .all()
    )
    skills = [r[0] for r in rows if r[1] == TAG_SKILL]
    attrs = [r[0] for r in rows if r[1] != TAG_SKILL]
    return skills, attrs


def set_user_tags(db: Session, user_id: int, skills: list[str], attrs: list[str]) -> None:
    db.query(UserTag).filter(UserTag.user_id == user_id).delete()
    for s in skills:
        tag = get_or_create_tag(db, s, TAG_SKILL)
        db.add(UserTag(user_id=user_id, tag_id=tag.id))
    for a in attrs:
        tag = get_or_create_tag(db, a, TAG_ROLE)
        db.add(UserTag(user_id=user_id, tag_id=tag.id))


def get_team_tags(db: Session, team_id: int) -> list[str]:
    rows = (
        db.query(Tag.name)
        .join(TeamTag, TeamTag.tag_id == Tag.id)
        .filter(TeamTag.team_id == team_id)
        .all()
    )
    return [r[0] for r in rows]


def set_team_tags(db: Session, team_id: int, names: list[str]) -> None:
    db.query(TeamTag).filter(TeamTag.team_id == team_id).delete()
    for n in names:
        tag = get_or_create_tag(db, n, TAG_OTHER)
        db.add(TeamTag(team_id=team_id, tag_id=tag.id))


def serialize_user(db: Session, user: User):
    from .schemas import UserOut
    skills, attrs = get_user_tags(db, user.id)
    return UserOut(
        id=user.id,
        student_id=user.student_no,
        name=user.nickname or "",
        school=user.school or "",
        major=user.major or "",
        grade=user.grade or "",
        skills=skills,
        attrs=attrs,
        phone=user.phone or "",
        created_at=user.created_at,
    )


def _active_members(db: Session, team_id: int) -> list[TeamMember]:
    return (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.leave_at.is_(None))
        .all()
    )


def serialize_team(db: Session, team: Team) -> dict:
    captain = db.get(User, team.captain_id)
    comp = db.get(Competition, team.competition_id) if team.competition_id else None
    members = _active_members(db, team.id)
    captain_member = next((m for m in members if m.role == 1), None)
    return {
        "id": team.id,
        "name": team.name,
        "leader_id": team.captain_id,
        "leader_name": captain.nickname if captain else "",
        "event_name": comp.name if comp else "",
        "school": captain.school if captain else "",
        "desc": team.description or "",
        "status": TEAM_STATUS_MAP.get(team.status, "招募中"),
        "max_members": team.max_members,
        "tags": get_team_tags(db, team.id),
        "members_count": len(members),
        "created_at": captain_member.joined_at if captain_member else None,
    }


def serialize_team_members(db: Session, team_id: int) -> list:
    from .schemas import MemberBrief
    briefs = []
    for m in _active_members(db, team_id):
        u = db.get(User, m.user_id)
        if not u:
            continue
        skills, _ = get_user_tags(db, u.id)
        briefs.append(MemberBrief(
            user_id=u.id,
            name=u.nickname or "",
            school=u.school or "",
            grade=u.grade or "",
            skills=skills,
            is_leader=(m.role == 1),
        ))
    return briefs


def serialize_notification(n: Notification):
    from .schemas import NotificationOut
    return NotificationOut(
        id=n.id,
        type=NOTI_TYPE_MAP.get(n.type, "system"),
        title=NOTI_TITLE_MAP.get(n.type, "通知"),
        content=n.content,
        is_read=bool(n.is_read),
        action_type=n.related_type or "",
        related_id=n.related_id or 0,
        created_at=n.created_at,
    )
