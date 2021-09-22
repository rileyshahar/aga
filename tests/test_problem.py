"""Tests the for `problem` module."""

import pytest

from core import problem
from core import test_case as case  # renamed so pytest doesn't run it as a test


def test_square() -> None:
    @case(4)
    @case(2, output=4)
    @case(-2, output=4)
    @problem
    def square(x: int) -> int:
        """Square x."""
        return x * x

    square.run_golden_tests()


def test_diff() -> None:
    @case(17, 10)
    @case(2, 4, output=-2)
    @case(3, 1, output=2)
    @problem
    def diff(x: int, y: int) -> int:
        """Compute x - y."""
        return x - y

    diff.run_golden_tests()


def test_failed_golden_test() -> None:
    @case(2, 4, output=-2)
    @case(3, 1, output=1)  # this is wrong, so the test should fail
    @problem
    def diff_should_fail(x: int, y: int) -> int:
        """Compute x - y."""
        return x - y

    with pytest.raises(AssertionError):
        diff_should_fail.run_golden_tests()
