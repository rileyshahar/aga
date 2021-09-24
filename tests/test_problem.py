"""Tests the for `Problem` class."""

from typing import TypeVar

from pytest import raises

from aga import Problem

Output = TypeVar("Output")


def test_valid_problem(valid_problem: Problem[Output]) -> None:
    """Test that correctly-defined problems succeed their golden tests."""
    valid_problem.run_golden_tests()


def test_failed_golden_test(diff_bad_gt: Problem[int]) -> None:
    """Ensure incorrect golden tests fail for a working diff implementation."""
    with raises(AssertionError):
        diff_bad_gt.run_golden_tests()


def test_bad_diff_impl(diff_bad_impl: Problem[int]) -> None:
    """Ensure golden tests fail for an incorrect diff implementation."""
    with raises(AssertionError):
        diff_bad_impl.run_golden_tests()
