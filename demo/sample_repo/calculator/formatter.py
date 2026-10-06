"""Output formatting utilities."""


def format_result(result: float, precision: int = 2) -> str:
    """Format a numeric result for display."""
    if result == int(result):
        return str(int(result))
    return f"{result:.{precision}f}"


def format_operation(op: str, a: float, b: float, result: float) -> str:
    """Format an operation as a readable string."""
    symbols = {"add": "+", "subtract": "-", "multiply": "×", "divide": "÷"}
    symbol = symbols.get(op, "?")
    return f"{format_result(a)} {symbol} {format_result(b)} = {format_result(result)}"


def format_history(history: list) -> str:
    """Format calculation history."""
    if not history:
        return "No calculations performed."
    lines = []
    for i, entry in enumerate(history, 1):
        line = f"{i}. {format_operation(entry['op'], entry['a'], entry['b'], entry['result'])}"
        lines.append(line)
    return "\n".join(lines)
