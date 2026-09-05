import pytest

from llm_tools_demo.calculator import calculate


@pytest.mark.parametrize(
    ("operation", "left", "right", "expected"),
    [
        ("+", 2, 3, 5),
        ("-", 7, 4, 3),
        ("*", 3, 5, 15),
        ("/", 8, 2, 4),
        ("%", 7, 3, 1),
        ("**", 2, 3, 8),
        ("*", -2, 3, -6),
        ("+", 5.5, 1.25, 6.75),
        ("**", 9, 0, 1),
        ("%", -7, 4, 1),
        ("**", 2, -2, 0.25),
        ("%", 7.5, 2, 1.5),
    ],
)
def test_calculate_supported_operations(
    operation: str,
    left: float,
    right: float,
    expected: float,
) -> None:
    assert calculate(operation, left, right) == expected  # type: ignore[arg-type]


def test_calculate_rejects_division_by_zero() -> None:
    with pytest.raises(ZeroDivisionError, match="除数不能为 0"):
        calculate("/", 10, 0)


def test_calculate_rejects_modulo_by_zero() -> None:
    with pytest.raises(ZeroDivisionError, match="取模运算的除数不能为 0"):
        calculate("%", 10, 0)


def test_calculate_rejects_unknown_operation() -> None:
    with pytest.raises(ValueError, match="不支持的运算符"):
        calculate("unknown", 1, 2)  # type: ignore[arg-type]
