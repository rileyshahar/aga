"""Tests for the `AutograderTestCase` class."""

from unittest import TestCase

from aga import Problem


def square_wrong(x: int) -> int:
    """Square x, incorrectly."""
    return x + 1


def square_right(x: int) -> int:
    """Square x, correctly."""
    return x ** 2


def test_square_wrong(square: Problem):
    """Test that the tests fail for the incorrect implementation."""
    suite = square.generate_test_suite(square_wrong)
    result = suite.run(TestCase().defaultTestResult())
    assert not result.wasSuccessful()


def test_square_right(square: Problem):
    """Test that the tests succeed for the correct implementation."""
    suite = square.generate_test_suite(square_right)
    result = suite.run(TestCase().defaultTestResult())
    assert result.wasSuccessful()
