from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    completed: bool = False


class TodoStore:
    def __init__(self) -> None:
        self._todos: list[Todo] = []
        self._next_id = 1

    def add(self, title: str) -> Todo:
        clean_title = title.strip()

        if clean_title == "":
            raise ValueError("待办标题不能为空")

        new_todo = Todo(
            id=self._next_id,
            title=clean_title,
        )

        self._todos.append(new_todo)
        self._next_id += 1

        return new_todo

    def list_all(self) -> list[Todo]:
        return self._todos.copy()

    def complete(self, todo_id: int) -> Todo:
        for todo in self._todos:
            if todo.id == todo_id:
                todo.completed = True
                return todo
        raise ValueError("待办事项不存在")
