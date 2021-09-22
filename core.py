from typing import Any, Callable, Generic, Optional, TypeVar
from unittest import TestCase

O = TypeVar("O")


def test_case(
    *args, output: Optional[Any] = None, **kwargs
) -> Callable[[Problem[O]], Problem[O]]:
    """Declare a specific test case for some problem.

    If `output` is None, the inputs will be tested against the wrapped function,
    the "golden solution" to the problem. If `output` is specified, the inputs
    will double as a test _of_ the golden solution; to successfully produce the
    problem grader, the golden solution must return output from the given input.
    """

    def outer(problem: Problem[O]) -> Problem[O]:
        if output is not None:
            problem.add_golden_test_case(GoldenTestInputs(output, *args, *kwargs))
            return problem

        else:
            problem.add_test_case(TestInputs(*args, **kwargs))
            return problem

    return outer


class TestInputs:
    def __init__(self, *args, **kwargs) -> None:

        self._args: tuple = args
        self._kwargs: dict = kwargs

    def _eval(self, func: Callable[..., O]) -> O:
        """Evaluate func on the arguments."""
        return func(*self._args, **self._kwargs)

    def check(self, golden: Callable[..., O], under_test: Callable[..., O]) -> bool:
        """Compare the output of `golden` to that of `under_test`.

        Returns `true` if the test succeeded (the outputs were identical),
        `false` otherwise.

        TODO: This should return more detailed information about the failure.
        """
        return self._eval(golden) == self._eval(under_test)


class GoldenTestInputs(TestInputs):
    def __init__(self, output: O, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)
        self._output = output

    def check_one(self, under_test: Callable[..., O]) -> bool:
        """Compare the output of `under_test` to the test case's golden output.

        Returns `true` if the test succeeded (the output was identical), `false`
        otherwise.

        TODO: This should return more detailed information about the failure.
        """
        return self._eval(under_test) == self._output


def problem(func: Callable[..., O]) -> Problem[O]:
    """Declare a function as the golden solution to a problem.

    This takes a function from I -> O and produces a `Problem[I, O]`.
    """
    return Problem(func)


class Problem(Generic[O]):
    """Represents a single problem."""

    def __init__(self, golden: Callable[..., O]) -> None:
        self._golden: Callable[..., O] = golden
        self._test_cases: list[TestInputs] = []
        self._golden_test_cases: list[GoldenTestInputs] = []

    def add_test_case(self, tc: TestInputs) -> None:
        """Add a test case to the problem.

        Student solutions will be checked against the golden solution; i.e.,
        this method does _not_ produce a test of the golden solution.
        """
        self._test_cases.append(tc)

    def add_golden_test_case(self, gtc: GoldenTestInputs) -> None:
        """Add a golden test case to the problem.

        Student solutions will be checked against the golden solution, and both
        against the output pasted to the GoldenTestInputs constructor; i.e., this
        method _does_ produce a test of the golden solution.
        """
        self._golden_test_cases.append(gtc)

    def run_golden_tests(self) -> None:
        """Run all tests of the golden solution."""
        for tc in self._golden_test_cases:
            assert tc.check_one(self._golden)



