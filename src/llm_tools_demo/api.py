from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from llm_tools_demo.todo import Todo, TodoStore


class TodoCreate(BaseModel):
    title: str


app = FastAPI(title="LLM Todo API")
store = TodoStore()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/todos")
def list_todos() -> list[Todo]:
    return store.list_all()


@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate) -> Todo:
    try:
        return store.add(data.title)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@app.patch("/todos/{todo_id}/complete")
def complete_todo(todo_id: int) -> Todo:
    try:
        return store.complete(todo_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int) -> None:
    try:
        store.delete(todo_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
