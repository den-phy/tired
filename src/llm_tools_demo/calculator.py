"""A small, explicit calculator implementation.

The calculator intentionally uses an operation allowlist instead of ``eval``.
This is the same boundary we will later apply to LLM-generated tool arguments:
validate first, then execute a known function.
"""

from typing import Literal

Operation = Literal["+", "-", "*", "/"]


def calculate(operation: Operation, left: float, right: float) -> float:
    """Calculate a result for one supported binary operation.

    Args:
        operation: A supported operation symbol.
        left: The left operand.
        right: The right operand.

    Raises:
        ValueError: If ``operation`` is unsupported.
        ZeroDivisionError: If dividing by zero.
    """
    if operation == "+":
        return left + right
    if operation == "-":
        return left - right
    if operation == "*":
        return left * right
    if operation == "/":
        if right == 0:
            raise ZeroDivisionError("除数不能为 0")
        return left / right

    raise ValueError(f"不支持的运算符: {operation}")


# TODO(day 1): Add the modulo (%) operation with zero-divisor validation.
# TODO(day 1): Add the exponentiation (**) operation and corresponding tests.

