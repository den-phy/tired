from sqlalchemy import select

from llm_tools_demo.database import SessionLocal
from llm_tools_demo.models import TodoModel


def main() -> None:
    with SessionLocal() as session:
        new_todo = TodoModel(title="学习 SQLAlchemy Session")

        session.add(new_todo)
        session.commit()
        session.refresh(new_todo)

        print(
            "created:",
            new_todo.id,
            new_todo.title,
            new_todo.completed,
        )

    with SessionLocal() as session:
        statement = select(TodoModel).order_by(TodoModel.id)
        todos = session.scalars(statement).all()

        for todo in todos:
            print(
                "saved:",
                todo.id,
                todo.title,
                todo.completed,
            )
    with SessionLocal() as session:
        todo = session.get(TodoModel, 1)

        if todo is None:
            raise ValueError("Todo 不存在")

        todo.completed = True
        session.commit()
        session.refresh(todo)

        print(
            "updated:",
            todo.id,
            todo.title,
            todo.completed,
        )


if __name__ == "__main__":
    main()
