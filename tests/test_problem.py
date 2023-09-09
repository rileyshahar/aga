"""Tests the for `Problem` class."""

from typing import Any

from pytest import raises

from aga import problem
from aga import test_case as case
from aga.core import Problem, test_case

AnyProblem = Problem[Any, Any]


def test_valid_problem(valid_problem: AnyProblem) -> None:
    """Test that correctly-defined problems succeed their golden tests."""
    valid_problem.check()


def test_square_metadata(square: AnyProblem) -> None:
    """Test that `square` has correct metadata."""
    assert square.name() == "square"
    assert square.expected_symbol() == "square"


def test_diff_metadata(diff: AnyProblem) -> None:
    """Test that `diff` has correct metadata."""
    assert diff.name() == "difference"
    assert diff.expected_symbol() == "difference"


def test_palindrome_metadata(palindrome: AnyProblem) -> None:
    """Test that `palindrome` has correct metadata.

    Note that palindrome uses the problem decorator's "name" argument.
    """
    assert palindrome.name() == "palindrome"
    assert palindrome.expected_symbol() == "strpal"


def test_failed_golden_test(diff_bad_gt: AnyProblem) -> None:
    """Ensure incorrect golden tests fail for a working diff implementation."""
    with raises(AssertionError):
        diff_bad_gt.check()


def test_bad_diff_impl(diff_bad_impl: AnyProblem) -> None:
    """Ensure golden tests fail for an incorrect diff implementation."""
    with raises(AssertionError):
        diff_bad_impl.check()


def test_reserved_kwarg() -> None:
    """Test that test_cases raises a value error if a reserved keyword is used."""
    with raises(ValueError):

        @case(aga_input="foo")
        @problem()
        def reserved_kwd(aga_input: str = "") -> str:
            """For testing a reserved keyword argument to `test_case`."""
            return aga_input


def test_problem_caller() -> None:
    """Test that the problem decorator returns the function it decorates."""

    @test_case(1)
    @problem()
    def test_problem(i: int) -> int:
        return i * i

    assert test_problem(10) == 10 * 10


def test_aga_stdout_check(aga_expect_stdout: AnyProblem) -> None:
    """Test that the problem decorator returns the function it decorates."""
    aga_expect_stdout.check()


def test_aga_expect_stdout_with_input(
    script_aga_expect_stdout_with_input: AnyProblem,
    function_aga_expect_stdout_with_input: AnyProblem,
) -> None:
    """Test that the problem decorator returns the function it decorates."""
    script_aga_expect_stdout_with_input.check()
    function_aga_expect_stdout_with_input.check()


def test_aga_expect_stdout_bad() -> None:
    """Test that the problem decorator returns the function it decorates."""
    with raises(AssertionError):

        @test_case(aga_expect_stdout="foo")
        @problem()
        def aga_expect_stdout_bad() -> None:
            """For testing a reserved keyword argument to `test_case`."""
            print("foo")

        aga_expect_stdout_bad.check()
