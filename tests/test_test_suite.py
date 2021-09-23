"""Tests for the `AutograderTestCase` class."""

from unittest import TestCase

from core import problem
from core import test_case as case  # renamed so pytest doesn't run it as a test


@case(4)
@case(2, output=4)
@case(-2, output=4)
@problem
def square(x: int) -> int:
    """Square x."""
    return x * x


def square_wrong(x: int) -> int:
    return x + 1


def square_right(x: int) -> int:
    return x ** 2


def test_square_wrong():
    suite = square.generate_test_suite(square_wrong)
    result = suite.run(TestCase().defaultTestResult())
    assert not result.wasSuccessful()

def test_square_right():
    suite = square.generate_test_suite(square_right)
    result = suite.run(TestCase().defaultTestResult())
    assert result.wasSuccessful()
