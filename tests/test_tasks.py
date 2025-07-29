# tests/test_tasks.py
from datetime import datetime, timedelta

def auth_headers(client):
    res = client.post("/auth/register", json={"email": "user1@example.com", "password": "pass"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_and_list_tasks(client):
    headers = auth_headers(client)
    # CREATE TASK
    due_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    res = client.post("/tasks/", json={"title": "Test Task", "description": "Desc", "due_date": due_date}, headers=headers)
    assert res.status_code == 200
    task = res.json()
    assert task["title"] == "Test Task"
    assert task["is_completed"] is False

    # LIST TASKS
    res = client.get("/tasks/", headers=headers)
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1

def test_permissions_cannot_delete_other_users_task(client):
    # User 1 buat task
    headers1 = auth_headers(client)
    res = client.post("/tasks/", json={"title": "User1 Task"}, headers=headers1)
    task_id = res.json()["id"]

    # User 2 login
    res2 = client.post("/auth/register", json={"email": "user2@example.com", "password": "pass"})
    headers2 = {"Authorization": f"Bearer {res2.json()['access_token']}"}

    # User 2 coba hapus task user1
    res = client.delete(f"/tasks/{task_id}", headers=headers2)
    assert res.status_code == 404  # Task tidak ditemukan (bukan milik dia)

def test_filtering_by_status(client):
    headers = auth_headers(client)
    # Buat task overdue & completed
    past_due = (datetime.utcnow() - timedelta(days=1)).isoformat()
    client.post("/tasks/", json={"title": "Overdue Task", "due_date": past_due}, headers=headers)
    client.post("/tasks/", json={"title": "Completed Task", "is_completed": True}, headers=headers)

    # Filter is_completed
    res = client.get("/tasks/?is_completed=true", headers=headers)
    tasks = res.json()
    assert all(task["is_completed"] for task in tasks)
