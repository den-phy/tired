from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from llm_tools_demo.api import app
from llm_tools_demo.database import Base, get_db


@pytest.fixture
def client() -> Generator[TestClient]:
    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)

    def override_get_db() -> Generator[Session]:
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    test_engine.dispose()


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_todos_return_ok(client: TestClient) -> None:
    response = client.get("/todos")

    assert response.status_code == 200
    assert response.json() == []


def test_create_todo_returns_created_todo(client: TestClient) -> None:
    response = client.post(
        "/todos",
        json={"title": "学习FastAPI"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "学习FastAPI",
        "completed": False,
    }


def test_create_todo_rejects_missing_title(client: TestClient) -> None:
    response = client.post("/todos", json={})
    body = response.json()
    assert response.status_code == 422
    assert body["detail"][0]["type"] == "missing"
    assert body["detail"][0]["loc"] == ["body", "title"]


def test_create_todo_rejects_blank_title(client: TestClient) -> None:
    response = client.post(
        "/todos",
        json={"title": "   "},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "待办标题不能为空"}


def test_complete_todo_returns_completed_todo(client: TestClient) -> None:
    create_response = client.post(
        "/todos",
        json={"title": "学习路径参数"},
    )
    todo_id = create_response.json()["id"]

    response = client.patch(f"/todos/{todo_id}/complete")

    assert response.status_code == 200
    assert response.json() == {
        "id": todo_id,
        "title": "学习路径参数",
        "completed": True,
    }


def test_complete_missing_todo_returns_not_found(client: TestClient) -> None:
    response = client.patch("/todos/999999/complete")

    assert response.status_code == 404
    assert response.json() == {"detail": "待办事项不存在"}


def test_delete_todo_removes_todo(client: TestClient) -> None:
    create_response = client.post(
        "/todos",
        json={"title": "稍后删除"},
    )
    todo_id = create_response.json()["id"]

    response = client.delete(f"/todos/{todo_id}")

    assert response.status_code == 204
    assert response.content == b""

    list_response = client.get("/todos")
    remaining_ids = [todo["id"] for todo in list_response.json()]
    assert todo_id not in remaining_ids


def test_delete_missing_todo_returns_not_found(client: TestClient) -> None:
    response = client.delete("/todos/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "待办事项不存在"}
