"""Tests the for `Problem` class."""

from pytest import raises

from core import Problem


def test_square(square: Problem):
    """Test golden tests for a working square implementation."""
    square.run_golden_tests()


def test_diff(diff: Problem):
    """Test golden tests for a working diff implementation."""
    diff.run_golden_tests()


def test_failed_golden_test(diff_bad_gt: Problem):
    """Ensure incorrect golden tests fail for a working diff implementation."""
    with raises(AssertionError):
        diff_bad_gt.run_golden_tests()


def test_bad_diff_impl(diff_bad_impl: Problem):
    """Ensure golden tests fail for an incorrect diff implementation."""
    with raises(AssertionError):
        diff_bad_impl.run_golden_tests()
