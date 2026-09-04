"""建表与种子数据初始化"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine
from .models import Competition, User


def init_db() -> None:
    """创建所有表（幂等），并写入演示赛事"""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        exists = conn.execute(select(Competition.id).limit(1)).first()
        if exists is None:
            with Session(engine) as session:
                demo_comps = [
                    Competition(name="全国大学生数学建模竞赛", category="数学建模类",
                                organizer="全国大学生数学建模竞赛组委会",
                                description="面向全国大学生的数学建模竞赛，三人一队，72 小时完成建模与论文。",
                                signup_end=datetime(2026, 9, 10)),
                    Competition(name="ACM-ICPC 国际大学生程序设计竞赛", category="算法类",
                                organizer="ACM 国际大学生程序设计竞赛组委会",
                                description="算法与编程能力的巅峰对决，三人一队现场解题。",
                                signup_end=datetime(2026, 10, 1)),
                    Competition(name="挑战杯中国大学生创业计划竞赛", category="创新创业类",
                                organizer="共青团中央",
                                description="鼓励大学生创业实践，跨学科组队，提交商业计划书。",
                                signup_end=datetime(2026, 5, 20)),
                    Competition(name="中国大学生计算机设计大赛", category="软件设计类",
                                organizer="教育部高等学校计算机类专业教学指导委员会",
                                description="涵盖软件应用与开发、数媒设计等多个赛道。",
                                signup_end=datetime(2026, 6, 15)),
                    Competition(name="全国大学生电子设计竞赛", category="电子设计类",
                                organizer="教育部高等教育司",
                                description="电子系统设计综合能力竞赛，四人一队。",
                                signup_end=datetime(2026, 8, 1)),
                ]
                for c in demo_comps:
                    session.add(c)
                session.commit()


def create_demo_user() -> User | None:
    """创建演示账号（可在脚本中调用）"""
    from .core.security import hash_password
    from .serializers import set_user_tags
    with Session(engine) as session:
        if session.query(User).filter(User.student_no == "20260001").first():
            return None
        user = User(
            student_no="20260001",
            nickname="演示同学",
            school="示例大学",
            major="计算机科学与技术",
            grade="2026级",
            password=hash_password("123456"),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        set_user_tags(session, user.id, ["Python", "深度学习"], ["熬夜冠军"])
        session.commit()
        return user
