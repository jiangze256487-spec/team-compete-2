"""FastAPI 应用入口"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import (
    auth_router, events_router, notifications_router, teams_router, users_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时自动建表（含内置分类种子）
    from .seed import init_db
    init_db()
    yield


app = FastAPI(title="竞赛组队系统 API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(teams_router)
app.include_router(events_router)
app.include_router(notifications_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
