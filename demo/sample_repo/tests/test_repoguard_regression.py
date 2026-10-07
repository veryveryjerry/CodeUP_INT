import pytest
from calculator.advanced import AdvancedCalculator


@pytest.fixture
def adv_calc():
    return AdvancedCalculator()


class TestPower:
    def test_power_basic(self, adv_calc):
        assert adv_calc.power(2, 3) == 8

    def test_power_zero(self, adv_calc):
        assert adv_calc.power(5, 0) == 1


class TestSqrt:
    def test_sqrt_positive(self, adv_calc):
        assert adv_calc.sqrt(9) == 3.0

    def test_sqrt_zero(self, adv_calc):
        assert adv_calc.sqrt(0) == 0.0

    def test_sqrt_negative(self, adv_calc):
        with pytest.raises(ValueError):
            adv_calc.sqrt(-1)


class TestPercentage:
    def test_percentage(self, adv_calc):
        assert adv_calc.percentage(200, 15) == 30.0


class TestAverage:
    def test_average_basic(self, adv_calc):
        assert adv_calc.average([10, 20, 30]) == 20.0

    def test_average_single(self, adv_calc):
        assert adv_calc.average([5]) == 5.0

    def test_average_empty(self, adv_calc):
        with pytest.raises(ValueError):
            adv_calc.average([])