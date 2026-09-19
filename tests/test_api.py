import logging
from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from llm_tools_demo.api import app
from llm_tools_demo.database import Base, get_db
from llm_tools_demo.repository import TodoRepository


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

    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as test_client:
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
    assert body["code"] == "validation_error"
    assert body["message"] == "请求参数校验失败"
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert body["details"][0]["loc"] == ["body", "title"]


def test_create_todo_rejects_blank_title(client: TestClient) -> None:
    response = client.post(
        "/todos",
        json={"title": "   "},
    )
    assert response.status_code == 400
    body = response.json()

    assert body["code"] == "bad_request"
    assert body["message"] == "待办标题不能为空"
    assert body["request_id"] == response.headers["X-Request-ID"]


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
    body = response.json()

    assert body["code"] == "not_found"
    assert body["message"] == "待办事项不存在"
    assert body["request_id"] == response.headers["X-Request-ID"]


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
    body = response.json()

    assert body["code"] == "not_found"
    assert body["message"] == "待办事项不存在"
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_request_id_from_client_is_returned(client: TestClient) -> None:
    response = client.get(
        "/health",
        headers={"X-Request-ID": "request-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "request-123"


def test_request_id_is_generated(client: TestClient) -> None:
    response = client.get("/health")

    request_id = response.headers["X-Request-ID"]
    parsed_request_id = UUID(request_id)

    assert parsed_request_id.version == 4
    assert str(parsed_request_id) == request_id


def test_request_log_contains_context(
    client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(
        logging.INFO,
        logger="llm_tools_demo.api",
    )

    response = client.get(
        "/health",
        headers={"X-Request-ID": "log-test-123"},
    )

    assert response.status_code == 200
    assert "request_id=log-test-123" in caplog.text
    assert "method=GET" in caplog.text
    assert "path=/health" in caplog.text
    assert "status_code=200" in caplog.text
    assert "elapsed_ms=" in caplog.text


def test_unexpected_error_returns_safe_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(
        logging.ERROR,
        logger="llm_tools_demo.api",
    )

    def raise_database_error(_: TodoRepository) -> None:
        raise RuntimeError("模拟数据库故障")

    monkeypatch.setattr(
        TodoRepository,
        "list_all",
        raise_database_error,
    )

    response = client.get(
        "/todos",
        headers={"X-Request-ID": "error-500"},
    )

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "error-500"
    assert response.json() == {
        "code": "internal_server_error",
        "message": "服务器内部错误",
        "request_id": "error-500",
    }
    assert "request_id=error-500" in caplog.text
    assert "method=GET" in caplog.text
    assert "path=/todos" in caplog.text
    assert "status_code=500" in caplog.text
    assert "elapsed_ms=" in caplog.text
    assert "error=RuntimeError" in caplog.text
    assert "模拟数据库故障" in caplog.text
