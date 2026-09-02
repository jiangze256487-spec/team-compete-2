"""建表与种子数据初始化"""
from .database import Base, engine
from .models import Event, EventCategory, User


def init_db() -> None:
    """创建所有表，并写入内置赛事分类与演示赛事"""
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
    with engine.connect() as conn:
        from sqlalchemy import select
        exists = conn.execute(select(Event.id).limit(1)).first()
        if exists is None:
            from sqlalchemy.orm import Session
            with Session(engine) as session:
                demo_events = [
                    Event(name="全国大学生数学建模竞赛", category="数学建模类",
                          org="全国大学生数学建模竞赛组委会", deadline="2026-09-10",
                          desc="面向全国大学生的数学建模竞赛，三人一队，72 小时完成建模与论文。"),
                    Event(name="ACM-ICPC 国际大学生程序设计竞赛", category="算法类",
                          org="ACM 国际大学生程序设计竞赛组委会", deadline="2026-10-01",
                          desc="算法与编程能力的巅峰对决，三人一队现场解题。"),
                    Event(name="挑战杯中国大学生创业计划竞赛", category="创新创业类",
                          org="共青团中央", deadline="2026-05-20",
                          desc="鼓励大学生创业实践，跨学科组队，提交商业计划书。"),
                    Event(name="中国大学生计算机设计大赛", category="软件设计类",
                          org="教育部高等学校计算机类专业教学指导委员会", deadline="2026-06-15",
                          desc="涵盖软件应用与开发、数媒设计等多个赛道。"),
                    Event(name="全国大学生电子设计竞赛", category="电子设计类",
                          org="教育部高等教育司", deadline="2026-08-01",
                          desc="电子系统设计综合能力竞赛，四人一队。"),
                ]
                for ev in demo_events:
                    session.add(ev)
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
