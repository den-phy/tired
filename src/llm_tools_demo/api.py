from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session

from llm_tools_demo.database import get_db
from llm_tools_demo.repository import TodoRepository

DatabaseSession = Annotated[Session, Depends(get_db)]


class TodoCreate(BaseModel):
    title: str


class TodoRead(BaseModel):
    id: int
    title: str
    completed: bool

    model_config = ConfigDict(from_attributes=True)


app = FastAPI(title="LLM Todo API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/todos")
def list_todos(session: DatabaseSession) -> list[TodoRead]:
    repository = TodoRepository(session)
    return repository.list_all()


@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(
    data: TodoCreate,
    session: DatabaseSession,
) -> TodoRead:
    repository = TodoRepository(session)
    try:
        todo_model = repository.add(data.title)
        return TodoRead.model_validate(todo_model)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.patch("/todos/{todo_id}/complete")
def complete_todo(todo_id: int, session: DatabaseSession) -> TodoRead:
    repository = TodoRepository(session)
    try:
        todo_model = repository.complete(todo_id)
        return TodoRead.model_validate(todo_model)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: DatabaseSession) -> None:
    repository = TodoRepository(session)
    try:
        return repository.delete(todo_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get("/db-health")
def database_health(session: DatabaseSession) -> dict[str, str]:
    database_name = session.execute(text("SELECT current_database()")).scalar_one()

    return {"database": database_name}
