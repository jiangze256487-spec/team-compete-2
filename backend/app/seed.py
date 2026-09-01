"""建表与种子数据初始化"""
from .database import Base, engine
from .models import EventCategory, User


def init_db() -> None:
    """创建所有表，并写入内置赛事分类"""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        from sqlalchemy import select
        exists = conn.execute(select(EventCategory.id).limit(1)).first()
        if exists is None:
            from sqlalchemy.orm import Session
            with Session(engine) as session:
                for name in ["算法类", "软件设计类", "创新创业类", "数学建模类", "电子设计类", "其他"]:
                    session.add(EventCategory(name=name))
                session.commit()


def create_demo_user() -> User | None:
    """创建演示账号（可在脚本中调用）"""
    from .core.security import hash_password
    with Session(engine) as session:
        if session.query(User).filter(User.student_id == "20260001").first():
            return None
        user = User(
            student_id="20260001",
            name="演示同学",
            school="示例大学",
            major="计算机科学与技术",
            grade="2026级",
            password_hash=hash_password("123456"),
            skills='["Python", "深度学习"]',
            attrs='["熬夜冠军"]',
        )
        session.add(user)
        session.commit()
        return user
