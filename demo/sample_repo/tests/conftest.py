"""Shared test fixtures."""
import pytest
from calculator.core import Calculator
from calculator.advanced import AdvancedCalculator


@pytest.fixture
def calculator():
    """Provide a fresh Calculator instance."""
    return Calculator()


@pytest.fixture
def advanced_calculator():
    """Provide a fresh AdvancedCalculator instance."""
    return AdvancedCalculator()
