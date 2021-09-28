"""Tests for the `AutograderTestCase` class."""

from typing import List, Tuple
from unittest import TestCase

import pytest

from aga import problem, test_case
from aga.core import Problem


def square_wrong(x: int) -> int:
    """Square x, incorrectly."""
    return x + 1


def square_right(x: int) -> int:
    """Square x, correctly."""
    return x ** 2


@test_case(2)
@problem()
def square_one_tc(x: int) -> int:
    """Square x.

    This problem has only one test case to make inspecting the specific error message
    easier.
    """
    return x * x


@test_case(x=2)
@problem()
def square_one_tc_kwd(x: int = 0) -> int:
    """Square x.

    This problem has only one test case to make inspecting the specific error message
    easier. It also uses a kewyork argument to allow testing that case.
    """
    return x * x


@test_case(2, 1)
@problem()
def diff_one_tc(x: int, y: int) -> int:
    """Compute x - y.

    This problem has only one test case to make inspecting the specific error message
    easier.
    """
    return x - y


@test_case(2, y=1)
@problem()
def diff_one_tc_kwd(x: int, y: int = 0) -> int:
    """Compute x - y.

    This problem has only one test case to make inspecting the specific error message
    easier. It also uses a keyword argument to allow testing combining positional and
    keyword args.
    """
    return x - y


def diff_wrong(x: int, y: int) -> int:
    """Compute x - y, incorrectly."""
    return x + y


def test_square_wrong(square: Problem[int]) -> None:
    """Test that the tests fail for the incorrect implementation."""
    suite = square.generate_test_suite(square_wrong)
    result = suite.run(TestCase().defaultTestResult())
    assert not result.wasSuccessful()


def test_square_right(square: Problem[int]) -> None:
    """Test that the tests succeed for the correct implementation."""
    suite = square.generate_test_suite(square_right)
    result = suite.run(TestCase().defaultTestResult())
    assert result.wasSuccessful()


@pytest.fixture(name="square_failure")
def fixture_square_failure() -> List[Tuple[TestCase, str]]:
    """Generate a list of failures for the single tc square problem."""
    suite = square_one_tc.generate_test_suite(square_wrong)
    result = suite.run(TestCase().defaultTestResult())

    return result.failures


def test_one_failure(square_failure: List[Tuple[TestCase, str]]) -> None:
    """Test that the one-tc problem only has one failure."""
    assert len(square_failure) == 1


def test_failure_message(square_failure: List[Tuple[TestCase, str]]) -> None:
    """Test that the one-tc problem's failure message is correct."""
    message = square_failure[0][1]
    assert "Checked with 2. Expected 4. Got 3 instead." in message


def test_failure_description(square_failure: List[Tuple[TestCase, str]]) -> None:
    """Test that the one-tc problem's test case description is correct."""
    message = square_failure[0][0].shortDescription()
    assert message == "Test 2"


@pytest.fixture(name="diff_failure")
def fixture_diff_failure() -> List[Tuple[TestCase, str]]:
    """Generate a list of failures for the single tc diff problem."""
    suite = diff_one_tc.generate_test_suite(diff_wrong)
    result = suite.run(TestCase().defaultTestResult())

    return result.failures


def test_one_failure_diff(diff_failure: List[Tuple[TestCase, str]]) -> None:
    """Test that the one-tc problem only has one failure."""
    assert len(diff_failure) == 1


def test_failure_message_multiple_args(
    diff_failure: List[Tuple[TestCase, str]]
) -> None:
    """Test that the one-tc diff problem's failure message is correct.

    This test is interesting because diff has two arguments, and we do formatting for
    tuples in `_TestInputs`.
    """
    message = diff_failure[0][1]
    assert "Checked with 2,1. Expected 1. Got 3 instead." in message


def test_failure_description_multiple_args(
    diff_failure: List[Tuple[TestCase, str]]
) -> None:
    """Test that the one-tc diff problem's test case description is correct.

    This test is interesting because diff has two arguments, and we do formatting for
    tuples in `_TestInputs`.
    """
    message = diff_failure[0][0].shortDescription()
    assert message == "Test 2,1"


@pytest.fixture(name="square_kwd_failure")
def fixture_square_kwd_failure() -> List[Tuple[TestCase, str]]:
    """Generate a list of failures for the single tc square kwd problem."""
    suite = square_one_tc_kwd.generate_test_suite(square_wrong)
    result = suite.run(TestCase().defaultTestResult())

    return result.failures


def test_one_failure_square_kwd(square_kwd_failure: List[Tuple[TestCase, str]]) -> None:
    """Test that the one-tc problem only has one failure."""
    assert len(square_kwd_failure) == 1


def test_failure_message_kwdargs(
    square_kwd_failure: List[Tuple[TestCase, str]]
) -> None:
    """Test that the one-tc square_kwd problem's failure message is correct.

    This test is interesting because square_kwd has a kewyord argument, and we do
    formatting for kwdargs in `_TestInputs`.
    """
    message = square_kwd_failure[0][1]
    assert "Checked with x=2. Expected 4. Got 3 instead." in message


def test_failure_description_kwdargs(
    square_kwd_failure: List[Tuple[TestCase, str]]
) -> None:
    """Test that the one-tc square_kwd problem's test case description is correct.

    This test is interesting because square_kwd has a kewyord argument, and we do
    formatting for kwdargs in `_TestInputs`.
    """
    message = square_kwd_failure[0][0].shortDescription()
    assert message == "Test x=2"


@pytest.fixture(name="diff_kwd_failure")
def fixture_diff_kwd_failure() -> List[Tuple[TestCase, str]]:
    """Generate a list of failures for the single tc diff kwd problem."""
    suite = diff_one_tc_kwd.generate_test_suite(diff_wrong)
    result = suite.run(TestCase().defaultTestResult())

    return result.failures


def test_one_failure_diff_kwd(diff_kwd_failure: List[Tuple[TestCase, str]]) -> None:
    """Test that the one-tc problem only has one failure."""
    assert len(diff_kwd_failure) == 1


def test_failure_message_pos_and_kwdargs(
    diff_kwd_failure: List[Tuple[TestCase, str]]
) -> None:
    """Test that the one-tc diff_kwd problem's failure message is correct.

    This test is interesting because diff_kwd has a kewyord argument and a positional
    argument.
    """
    message = diff_kwd_failure[0][1]
    assert "Checked with 2,y=1. Expected 1. Got 3 instead." in message


def test_failure_description_pos_and_kwdargs(
    diff_kwd_failure: List[Tuple[TestCase, str]]
) -> None:
    """Test that the one-tc diff_kwd problem's test case description is correct.

    This test is interesting because diff_kwd has a kewyord argument and a positional
    argument.
    """
    message = diff_kwd_failure[0][0].shortDescription()
    assert message == "Test 2,y=1"
