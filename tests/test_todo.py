import pytest

from llm_tools_demo.todo import TodoStore


def test_add_creates_todo() -> None:
    store = TodoStore()

    todo = store.add("  学习 Python  ")

    assert todo.id == 1
    assert todo.title == "学习 Python"
    assert todo.completed is False


def test_add_increments_ids() -> None:
    store = TodoStore()

    first = store.add("学习 Agent")
    second = store.add("学习大模型")

    assert first.id == 1
    assert second.id == 2


def test_add_rejects_blank_title() -> None:
    store = TodoStore()

    with pytest.raises(ValueError, match="待办标题不能为空"):
        store.add("    ")


def test_list_all_returns_empty_list() -> None:
    store = TodoStore()

    assert store.list_all() == []


def test_list_all_returns_todos_in_order() -> None:
    store = TodoStore()
    first = store.add("  我是甲 ")
    second = store.add("  我是乙 ")

    todos = store.list_all()

    assert len(todos) == 2
    assert todos[0] == first
    assert todos[1] == second


def test_complete_marks_selected_todo_completed() -> None:
    store = TodoStore()
    store.add("  第一次测试 ")
    store.add(" 第二次测试  ")
    store.complete(2)
    todos = store.list_all()
    first = todos[0]
    second = todos[1]
    assert second.id == 2
    assert second.completed is True
    assert first.completed is False


def test_complete_rejects_unknown_id() -> None:
    store = TodoStore()
    store.add("  第一次测试 ")
    store.add(" 第二次测试  ")
    with pytest.raises(ValueError, match="待办事项不存在"):
        store.complete(999)


def test_delete_removes_todo() -> None:
    store = TodoStore()
    todo = store.add(" 在学Delete ")
    store.delete(todo.id)
    assert store.list_all() == []


def test_delete_rejects_missing_todo() -> None:
    store = TodoStore()
    store.add("  在学Delete  ")
    with pytest.raises(ValueError, match="待办事项不存在"):
        store.delete(9999)


def test_delete_works_after_previous_deletion() -> None:
    store = TodoStore()
    first = store.add("第一项")
    second = store.add("第二项")

    store.delete(first.id)
    store.delete(second.id)

    assert store.list_all() == []
