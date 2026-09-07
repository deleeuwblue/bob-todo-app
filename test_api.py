import pytest
from fastapi.testclient import TestClient

from main import app, Base, engine

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_list_empty():
    r = client.get("/api/todos")
    assert r.status_code == 200
    assert r.json() == []


def test_create():
    r = client.post("/api/todos", json={"title": "Buy milk"})
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Buy milk"
    assert body["completed"] is False
    assert "id" in body
    assert "created_at" in body


def test_list_after_create():
    r = client.get("/api/todos")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_update_title():
    r = client.post("/api/todos", json={"title": "Original"})
    todo_id = r.json()["id"]
    r2 = client.patch(f"/api/todos/{todo_id}", json={"title": "Updated"})
    assert r2.status_code == 200
    assert r2.json()["title"] == "Updated"


def test_update_completed():
    r = client.post("/api/todos", json={"title": "Complete me"})
    todo_id = r.json()["id"]
    r2 = client.patch(f"/api/todos/{todo_id}", json={"completed": True})
    assert r2.status_code == 200
    assert r2.json()["completed"] is True


def test_delete():
    r = client.post("/api/todos", json={"title": "Delete me"})
    todo_id = r.json()["id"]
    r2 = client.delete(f"/api/todos/{todo_id}")
    assert r2.status_code == 204
    r3 = client.patch(f"/api/todos/{todo_id}", json={"title": "x"})
    assert r3.status_code == 404


def test_patch_not_found():
    r = client.patch("/api/todos/99999", json={"title": "ghost"})
    assert r.status_code == 404


def test_delete_not_found():
    r = client.delete("/api/todos/99999")
    assert r.status_code == 404
