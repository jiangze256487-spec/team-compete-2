# team-compete（竞赛组队系统）

一个竞赛组队平台：用户可以发布/浏览竞赛信息、创建或加入队伍、接收通知。

- 前端：Vue 3 + Vite + Pinia + Vue Router + Tailwind CSS + axios
- 后端：FastAPI + SQLAlchemy + MySQL（腾讯云 TDSQL-C）+ JWT 认证

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

### 1. 配置数据库连接（团队协作必需）

后端连的是团队共享的腾讯云 MySQL，需先配置连接串：

```bash
cd backend
cp .env.example .env        # 复制模板
# 编辑 .env，把 DATABASE_URL 里的「你的数据库密码」改成真实密码
```

> 密码含特殊字符需 URL 编码：`@` → `%40`，`!` → `%21`，`#` → `%23`，空格 → `%20`。
> 若数据库开启了 IP 白名单，需在腾讯云控制台把本机公网 IP 加入白名单。

### 2. 安装依赖并启动

```bash
pip install -r requirements.txt        # 建议使用虚拟环境（venv 或 conda）
uvicorn app.main:app --reload           # 默认监听 http://127.0.0.1:8000
```

- 未配置 `.env` 时，会自动回退到本地 SQLite（`compete_mate.db`）并建表，方便单机调试。
- 健康检查：访问 http://127.0.0.1:8000/api/health 返回 `{"status":"ok"}`。
- 交互式 API 文档：http://127.0.0.1:8000/docs

## 前端启动

```bash
cd frontend
npm install
npm run dev                              # 默认 http://localhost:5173
```

前端已配置代理：所有 `/api` 请求会转发到后端 `http://127.0.0.1:8000`，因此**请先启动后端再启动前端**。

## 配置说明

后端配置通过 `backend/.env` 加载（此文件已被 git 忽略，不会提交到仓库）。可配置项见 [backend/.env.example](backend/.env.example)：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `SECRET_KEY` | `dev-secret-change-in-production` | JWT 签名密钥（生产务必更换） |
| `DATABASE_URL` | `sqlite:///./compete_mate.db` | 数据库连接；团队协作需改成腾讯云 MySQL 连接串 |
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
