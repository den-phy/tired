from sqlalchemy import select
from sqlalchemy.orm import Session

from llm_tools_demo.models import TodoModel


class TodoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, title: str) -> TodoModel:
        clean_title = title.strip()

        if clean_title == "":
            raise ValueError("待办标题不能为空")

        todo = TodoModel(title=clean_title)

        self._session.add(todo)
        self._session.commit()
        self._session.refresh(todo)

        return todo

    def list_all(self) -> list[TodoModel]:
        statement = select(TodoModel).order_by(TodoModel.id)
        return list(self._session.scalars(statement).all())

    def get(self, todo_id: int) -> TodoModel:
        todo = self._session.get(TodoModel, todo_id)

        if todo is None:
            raise ValueError("待办事项不存在")

        return todo

    def complete(self, todo_id: int) -> TodoModel:
        todo = self.get(todo_id)
        todo.completed = True

        self._session.commit()
        self._session.refresh(todo)

        return todo

    def delete(self, todo_id: int) -> None:
        todo = self.get(todo_id)

        self._session.delete(todo)
        self._session.commit()
