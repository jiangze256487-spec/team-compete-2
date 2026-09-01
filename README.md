# team-compete（竞赛组队系统）

一个竞赛组队平台：用户可以发布/浏览竞赛信息、创建或加入队伍、接收通知。

- 前端：Vue 3 + Vite + Pinia + Vue Router + Tailwind CSS + axios
- 后端：FastAPI + SQLAlchemy + SQLite + JWT 认证

## 环境要求

- Python 3.11+（开发环境为 3.13）
- Node.js 18+

## 目录结构

```
team-compete/
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── main.py        # 应用入口（启动时自动建表 + 写入内置赛事分类）
│   │   ├── config.py      # 配置（含默认值，.env 可覆盖）
│   │   ├── database.py    # SQLAlchemy 连接与会话
│   │   ├── seed.py        # 建表、赛事分类种子、演示账号
│   │   ├── core/          # 安全（JWT、密码哈希）、依赖注入
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # Pydantic 请求/响应模型
│   │   └── routers/       # 路由（auth/users/teams/events/notifications）
│   ├── requirements.txt   # Python 依赖
│   └── smoke_test.py      # 冒烟测试
└── frontend/              # Vue 3 前端
    ├── src/               # 源码（views/components/api/stores/router）
    ├── vite.config.js     # Vite 配置（/api 代理到后端 8000）
    └── package.json       # 前端依赖与脚本
```

## 后端启动

```bash
cd backend
pip install -r requirements.txt        # 建议使用虚拟环境（venv 或 conda）
uvicorn app.main:app --reload           # 默认监听 http://127.0.0.1:8000
```

- 首次启动会自动创建 `compete_mate.db` 并建表、写入内置赛事分类，无需手动建库。
- 健康检查：访问 http://127.0.0.1:8000/api/health 返回 `{"status":"ok"}`。
- 交互式 API 文档：http://127.0.0.1:8000/docs

## 前端启动

```bash
cd frontend
npm install
npm run dev                              # 默认 http://localhost:5173
```

前端已配置代理：所有 `/api` 请求会转发到后端 `http://127.0.0.1:8000`，因此**请先启动后端再启动前端**。

## 配置（可选）

后端所有配置都有默认值，不配置也能直接运行。如需自定义，复制模板后修改：

```bash
cd backend
cp .env.example .env
```

可配置项见 [backend/.env.example](backend/.env.example)，主要包括：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `SECRET_KEY` | `dev-secret-change-in-production` | JWT 签名密钥（生产务必更换） |
| `DATABASE_URL` | `sqlite:///./compete_mate.db` | 数据库连接（生产可换 PostgreSQL） |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | 允许跨域的前端地址 |

## 演示账号

后端启动后，可手动创建演示账号（学号 `20260001`，密码 `123456`）：

```bash
cd backend
python -c "from app.seed import create_demo_user; create_demo_user()"
```

## 主要 API 路由

| 前缀 | 说明 |
|---|---|
| `/api/auth` | 注册、登录（JWT） |
| `/api/users` | 用户信息 |
| `/api/teams` | 队伍（创建/加入/申请） |
| `/api/events` | 赛事（发布/浏览） |
| `/api/notifications` | 通知 |

## 测试

```bash
cd backend
python smoke_test.py
```
