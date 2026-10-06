"""Tests for the core Calculator class."""
import pytest
from calculator.core import Calculator


@pytest.fixture
def calc():
    """Create a fresh Calculator instance."""
    return Calculator()


class TestAddition:
    def test_add_positive(self, calc):
        assert calc.add(2, 3) == 5

    def test_add_negative(self, calc):
        assert calc.add(-1, -1) == -2

    def test_add_zero(self, calc):
        assert calc.add(0, 5) == 5

    def test_add_floats(self, calc):
        assert calc.add(1.5, 2.5) == 4.0


class TestSubtraction:
    def test_subtract_positive(self, calc):
        assert calc.subtract(5, 3) == 2

    def test_subtract_negative(self, calc):
        assert calc.subtract(-1, -1) == 0

    def test_subtract_zero(self, calc):
        assert calc.subtract(5, 0) == 5


class TestMultiplication:
    def test_multiply_positive(self, calc):
        assert calc.multiply(3, 4) == 12

    def test_multiply_zero(self, calc):
        assert calc.multiply(5, 0) == 0

    def test_multiply_negative(self, calc):
        assert calc.multiply(-2, 3) == -6


class TestDivision:
    def test_divide_positive(self, calc):
        assert calc.divide(10, 2) == 5

    def test_divide_float(self, calc):
        assert calc.divide(7, 2) == 3.5

    def test_divide_negative(self, calc):
        assert calc.divide(-6, 3) == -2

    # NOTE: No test for division by zero — this is the TEST GAP
    # The agent should discover and add this test


class TestHistory:
    def test_history_records(self, calc):
        calc.add(1, 2)
        calc.multiply(3, 4)
        history = calc.get_history()
        assert len(history) == 2

    def test_clear_history(self, calc):
        calc.add(1, 2)
        calc.clear_history()
        assert len(calc.get_history()) == 0
