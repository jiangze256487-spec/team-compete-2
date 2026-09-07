"""后端冒烟测试：验证核心 API 全链路"""
import os
import sys
import tempfile

# 使用临时 SQLite，避免污染项目库
TMP_DB = os.path.join(tempfile.mkdtemp(), "smoke_test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TMP_DB}"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

passed = []


def ok(name):
    passed.append(name)
    print(f"  [PASS] {name}")


with TestClient(app) as client:
    print("== 冒烟测试开始 ==")

    # 1. 健康检查
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok", r.text
    ok("GET /api/health")

    # 2. 注册用户 A（队长）
    r = client.post("/api/auth/register", json={
        "student_id": "20260001", "password": "123456", "name": "张三",
        "school": "示例大学", "major": "计算机", "grade": "2026级",
        "phone": "13800000001",
    })
    assert r.status_code == 200, r.text
    token_a = r.json()["access_token"]
    ok("POST /api/auth/register (队长A)")

    # 3. 注册用户 B（队员）
    r = client.post("/api/auth/register", json={
        "student_id": "20260002", "password": "123456", "name": "李四",
        "school": "示例大学", "major": "软件工程", "grade": "2025级",
        "phone": "13800000002",
    })
    assert r.status_code == 200, r.text
    token_b = r.json()["access_token"]
    ok("POST /api/auth/register (队员B)")

    # 4. 登录
    r = client.post("/api/auth/login", json={"student_id": "20260001", "password": "123456"})
    assert r.status_code == 200, r.text
    ok("POST /api/auth/login")

    # 5. 错误密码登录
    r = client.post("/api/auth/login", json={"student_id": "20260001", "password": "wrong"})
    assert r.status_code == 401, r.text
    ok("POST /api/auth/login 错误密码 -> 401")

    # 6. 更新标签
    ha = {"Authorization": f"Bearer {token_a}"}
    r = client.put("/api/users/me/tags", headers=ha, json={"skills": ["Python", "深度学习"], "attrs": ["熬夜冠军"]})
    assert r.status_code == 200 and r.json()["skills"] == ["Python", "深度学习"], r.text
    ok("PUT /api/users/me/tags")

    # 7. 创建队伍（赛事须为 init_db 预置的竞赛）
    r = client.post("/api/teams", headers=ha, json={
        "name": "AI挑战赛战队", "event_name": "全国大学生数学建模竞赛",
        "desc": "招会深度学习的队友", "max_members": 4,
        "tags": ["Python", "深度学习", "算法"],
    })
    assert r.status_code == 201, r.text
    team_id = r.json()["id"]
    ok("POST /api/teams 创建队伍")

    # 8. 队伍列表（按技能筛选）
    r = client.get("/api/teams", params={"skill": "深度学习"})
    assert r.status_code == 200 and len(r.json()) == 1, r.text
    ok("GET /api/teams?skill=深度学习")

    # 9. 队伍详情
    r = client.get(f"/api/teams/{team_id}")
    assert r.status_code == 200 and r.json()["members_count"] == 1, r.text
    ok("GET /api/teams/{id} 详情含队长成员")

    # 10. 用户B申请入队
    hb = {"Authorization": f"Bearer {token_b}"}
    r = client.post(f"/api/teams/{team_id}/apply", headers=hb)
    assert r.status_code == 200, r.text
    ok("POST /api/teams/{id}/apply 申请入队")

    # 11. 队长查通知，同意申请
    r = client.get("/api/notifications", headers=ha)
    assert r.status_code == 200 and len(r.json()) == 1, r.text
    noti_id = r.json()[0]["id"]
    assert r.json()[0]["action_type"] == "request", r.text
    r = client.post(f"/api/notifications/{noti_id}/action", headers=ha, json={"action": "accept"})
    assert r.status_code == 200, r.text
    ok("POST /api/notifications/{id}/action 同意入队")

    # 12. 队伍人数应为2
    r = client.get(f"/api/teams/{team_id}")
    assert r.json()["members_count"] == 2, r.text
    ok("队伍成员数变为 2")

    # 13. 未授权访问
    r = client.get("/api/users/me")
    assert r.status_code == 401, r.text
    ok("未带 token 访问 /api/users/me -> 401")

    # 14. 赛事分类种子
    r = client.get("/api/events/categories")
    assert r.status_code == 200 and len(r.json()) >= 5, r.text
    ok("GET /api/events/categories 内置分类")

    # 15. 赛事创建与列表（用独立分类，避免与种子演示赛事冲突）
    r = client.post("/api/events", json={
        "name": "测试专用赛事", "category": "测试类",
        "org": "测试组委会", "deadline": "2026-09-30",
    })
    assert r.status_code == 201, r.text
    r = client.get("/api/events", params={"category": "测试类"})
    assert r.status_code == 200 and len(r.json()) == 1, r.text
    ok("POST/GET /api/events 赛事")

    # 16. 退出队伍
    r = client.post(f"/api/teams/{team_id}/leave", headers=hb)
    assert r.status_code == 200, r.text
    r = client.get(f"/api/teams/{team_id}")
    assert r.json()["members_count"] == 1, r.text
    ok("POST /api/teams/{id}/leave 退出队伍")

    # 17. 离队通知为告知类：action_type 必须为空（前端不应显示接受/拒绝按钮）
    r = client.get("/api/notifications", headers=ha)
    assert r.status_code == 200, r.text
    notis_a = r.json()
    leave_noti = next((x for x in notis_a if x["title"] == "离队通知"), None)
    assert leave_noti is not None, notis_a
    assert leave_noti["action_type"] == "", notis_a
    # 队长侧其余通知（已处理的申请等）也不应残留可操作标记
    assert all(x["action_type"] == "" for x in notis_a), notis_a
    ok("离队通知 action_type 为空")

    # 18. "你已加入队伍" 等告知类系统通知同样不可操作
    r = client.get("/api/notifications", headers=hb)
    assert r.status_code == 200, r.text
    notis_b = r.json()
    assert len(notis_b) >= 1, notis_b
    assert all(x["action_type"] == "" for x in notis_b), notis_b
    ok("告知类通知均无接受/拒绝标记")

print(f"\n== 冒烟测试完成：{len(passed)} 项通过 ==")
