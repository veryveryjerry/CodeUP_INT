"""Advanced math operations that depend on the core Calculator."""
import math
from calculator.core import Calculator


class AdvancedCalculator:
    """Advanced calculator extending basic operations."""

    def __init__(self):
        self.calc = Calculator()

    def power(self, base: float, exponent: float) -> float:
        """Calculate base raised to exponent."""
        result = base ** exponent
        return result

    def sqrt(self, n: float) -> float:
        """Calculate square root."""
        if n < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(n)

    def percentage(self, value: float, percent: float) -> float:
        """Calculate percentage of a value."""
        return self.calc.divide(self.calc.multiply(value, percent), 100)

    def average(self, numbers: list) -> float:
        """Calculate average of a list of numbers."""
        if not numbers:
            raise ValueError("Cannot calculate average of empty list")
        total = numbers[0]
        for n in numbers[1:]:
            total = self.calc.add(total, n)
        return self.calc.divide(total, len(numbers))

    def ratio(self, a: float, b: float) -> float:
        """Calculate ratio a:b as a/b."""
        return self.calc.divide(a, b)
