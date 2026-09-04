"""赛事路由（对应 competitions 表）"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Competition, Team
from ..schemas import CategoryOut, EventCreate, EventOut

router = APIRouter(prefix="/api/events", tags=["赛事"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(Competition.category).distinct().all()
    result = []
    for i, (cat,) in enumerate(rows):
        if cat:
            result.append(CategoryOut(id=i + 1, name=cat))
    return result


@router.get("", response_model=list[EventOut])
def list_events(category: str = "", db: Session = Depends(get_db)):
    query = db.query(Competition)
    if category:
        query = query.filter(Competition.category == category)
    comps = query.order_by(Competition.id.desc()).all()
    result = []
    for c in comps:
        result.append(EventOut(
            id=c.id,
            name=c.name,
            category=c.category or "",
            org=c.organizer or "",
            desc=c.description or "",
            deadline=c.signup_end.strftime("%Y-%m-%d") if c.signup_end else "",
            teams_count=db.query(Team).filter(Team.competition_id == c.id).count(),
        ))
    return result


@router.post("", response_model=EventOut, status_code=201)
def create_event(data: EventCreate, db: Session = Depends(get_db)):
    """赛事录入（管理员后台调用，当前未做角色鉴权）"""
    comp = Competition(
        name=data.name,
        category=data.category or None,
        organizer=data.org or None,
        description=data.desc or None,
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return EventOut(
        id=comp.id,
        name=comp.name,
        category=comp.category or "",
        org=comp.organizer or "",
        desc=comp.description or "",
        deadline="",
        teams_count=0,
    )
