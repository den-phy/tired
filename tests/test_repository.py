from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from llm_tools_demo.database import Base
from llm_tools_demo.repository import TodoRepository


@pytest.fixture
def session() -> Generator[Session]:
    test_engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session

    test_engine.dispose()


def test_repository_adds_and_lists_todo(session: Session) -> None:
    repository = TodoRepository(session)

    created = repository.add("  学习 Repository  ")
    todos = repository.list_all()

    assert created.id == 1
    assert created.title == "学习 Repository"
    assert created.completed is False

    assert len(todos) == 1
    assert todos[0].id == created.id


def test_repository_completes_todo(session: Session) -> None:
    repository = TodoRepository(session)
    created = repository.add("完成数据库练习")

    completed = repository.complete(created.id)

    assert completed.id == created.id
    assert completed.completed is True
    assert repository.get(created.id).completed is True


def test_repository_deletes_todo(session: Session) -> None:
    repository = TodoRepository(session)
    created = repository.add("删除数据库练习")

    repository.delete(created.id)

    with pytest.raises(ValueError, match="待办事项不存在"):
        repository.get(created.id)


def test_repository_rejects_missing_todo(session: Session) -> None:
    repository = TodoRepository(session)

    with pytest.raises(ValueError, match="待办事项不存在"):
        repository.get(999999)


def test_repository_rejects_blank_title(session: Session) -> None:
    repository = TodoRepository(session)

    with pytest.raises(ValueError, match="待办标题不能为空"):
        repository.add("   ")
