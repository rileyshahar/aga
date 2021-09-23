"""Contains various fixtures, especially pre-written problems."""

from pytest import fixture

from aga import Problem, problem, test_case


@fixture(name="square")
def fixture_square() -> Problem[int]:
    """Generate a basic, correct implementation of a square problem."""

    @test_case(4)
    @test_case(2, output=4)
    @test_case(-2, output=4)
    @problem
    def square(x: int) -> int:
        """Square x."""
        return x * x

    return square


@fixture(name="diff")
def fixture_diff() -> Problem[int]:
    """Generate a basic, correct implementation of a difference problem."""

    @test_case(17, 10)
    @test_case(2, 4, output=-2)
    @test_case(3, 1, output=2)
    @problem
    def difference(x: int, y: int) -> int:
        """Compute x - y."""
        return x - y

    return difference


@fixture(name="diff_bad_gt")
def fixture_diff_bad_gt(diff: Problem[int]) -> Problem[int]:
    """Generate an implementation of difference with an incorrect golden test."""
    return test_case(3, 1, output=1)(diff)


@fixture(name="diff_bad_impl")
def fixture_diff_bad_impl() -> Problem[int]:
    """Generate a difference problem with an incorrect implementation."""

    @test_case(17, 10)
    @test_case(2, 4, output=-2)
    @test_case(3, 1, output=2)
    @problem
    def diff_should_fail(x: int, y: int) -> int:
        """Compute x - y."""
        return x + y

    return diff_should_fail
