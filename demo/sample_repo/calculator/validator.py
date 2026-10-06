"""Input validation utilities."""


def validate_number(value) -> float:
    """Validate and convert input to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid number: {value}")


def validate_positive(value: float) -> float:
    """Validate that a number is positive."""
    num = validate_number(value)
    if num <= 0:
        raise ValueError(f"Expected positive number, got {num}")
    return num


def validate_non_negative(value: float) -> float:
    """Validate that a number is non-negative."""
    num = validate_number(value)
    if num < 0:
        raise ValueError(f"Expected non-negative number, got {num}")
    return num
