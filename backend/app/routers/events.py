"""赛事路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Event, EventCategory
from ..schemas import CategoryOut, EventCreate, EventOut

router = APIRouter(prefix="/api/events", tags=["赛事"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(EventCategory).all()


@router.get("", response_model=list[EventOut])
def list_events(category: str = "", db: Session = Depends(get_db)):
    query = db.query(Event)
    if category:
        query = query.filter(Event.category == category)
    return query.order_by(Event.created_at.desc()).all()


@router.post("", response_model=EventOut, status_code=201)
def create_event(data: EventCreate, db: Session = Depends(get_db)):
    """赛事录入（管理员后台调用，当前未做角色鉴权）"""
    event = Event(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
