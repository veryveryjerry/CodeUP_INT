"""
Demo Calculator Repository - A simple calculator with a known division-by-zero bug.
This serves as the built-in demo for RepoGuard AI.
"""


class Calculator:
    """A basic calculator supporting arithmetic operations."""

    def __init__(self):
        self.history = []

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append({"op": "add", "a": a, "b": b, "result": result})
        return result

    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        result = a - b
        self.history.append({"op": "subtract", "a": a, "b": b, "result": result})
        return result

    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = a * b
        self.history.append({"op": "multiply", "a": a, "b": b, "result": result})
        return result

    def divide(self, a: float, b: float) -> float:
        """Divide a by b.

        BUG: This function does not handle division by zero properly.
        It will raise an unhandled ZeroDivisionError instead of
        returning a meaningful error response.
        """
        # BUG: No check for b == 0
        result = a / b
        self.history.append({"op": "divide", "a": a, "b": b, "result": result})
        return result

    def get_history(self) -> list:
        """Return calculation history."""
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()
