"""Contains various fixtures, especially pre-written problems."""

from typing import List

import pytest
from _pytest.config import Config
from pytest_lazyfixture import lazy_fixture  # type: ignore

from aga import Problem, problem, test_case


def pytest_collection_modifyitems(config: Config, items: List[pytest.Item]) -> None:
    """Prevent pytest from running `slow` tests unless `-m "slow"` is passed."""
    keywordexpr = config.option.keyword
    markexpr = config.option.markexpr
    if keywordexpr or markexpr:
        return

    skip_slow = pytest.mark.skip(reason="`-m slow` not selected")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(
    params=[  # type: ignore
        lazy_fixture("square"),
        lazy_fixture("diff"),
        lazy_fixture("palindrome"),
    ]
)
def valid_problem(request):
    """Generate a parameterized test over a number of guaranteed-valid Problems."""
    return request.param


@pytest.fixture(name="square")
def fixture_square() -> Problem[int]:
    """Generate a problem which tests a square function."""

    @test_case(4)
    @test_case(2, output=4)
    @test_case(-2, output=4)
    @problem()
    def square(x: int) -> int:
        """Square x."""
        return x * x

    return square


@pytest.fixture(name="diff")
def fixture_diff() -> Problem[int]:
    """Generate a problem which tests a difference function."""

    @test_case(17, 10)
    @test_case(2, 4, output=-2)
    @test_case(3, 1, output=2)
    @problem()
    def difference(x: int, y: int) -> int:
        """Compute x - y."""
        return x - y

    return difference


@pytest.fixture(name="palindrome")
def fixture_palindrome() -> Problem[bool]:
    """Generate a problem which tests a string palindrome function.

    This problem uses the `name` argument to `problem` to declare a different name from
    the function it decorates.
    """

    @test_case("eve")
    @test_case("hello")
    @test_case("", output=True)
    @test_case("goodbye", output=False)
    @test_case("123454321", output=True)
    @problem(name="palindrome")
    def strpal(s: str) -> bool:
        """Determine whether s is a palindrome."""
        return s == s[::-1]

    return strpal


@pytest.fixture(name="diff_bad_gt")
def fixture_diff_bad_gt(diff: Problem[int]) -> Problem[int]:
    """Generate an implementation of difference with an incorrect golden test."""
    return test_case(3, 1, output=1)(diff)


@pytest.fixture(name="diff_bad_impl")
def fixture_diff_bad_impl() -> Problem[int]:
    """Generate a difference problem with an incorrect implementation."""

    @test_case(17, 10)
    @test_case(2, 4, output=-2)
    @test_case(3, 1, output=2)
    @problem()
    def diff_should_fail(x: int, y: int) -> int:
        """Compute x - y."""
        return x + y

    return diff_should_fail
