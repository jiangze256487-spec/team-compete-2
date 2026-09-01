"""认证路由：学号注册 / 登录"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.security import create_access_token, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import TokenOut, UserLogin, UserOut, UserRegister

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=TokenOut)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.student_id == data.student_id).first():
        raise HTTPException(status_code=400, detail="该学号已被注册")
    user = User(
        student_id=data.student_id,
        name=data.name,
        school=data.school,
        major=data.major,
        grade=data.grade,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == data.student_id).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="学号或密码错误")
    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))
