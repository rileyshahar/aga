"""Contains the problem decorator."""

from typing import TYPE_CHECKING, Callable, Generic, TypeVar

if TYPE_CHECKING:
    from .case import GoldenTestCase, TestCase


O = TypeVar("O")


def problem(func: Callable[..., O]) -> "Problem[O]":
    """Declare a function as the golden solution to a problem.

    This takes a function from I -> O and produces a `Problem[I, O]`.
    """
    return Problem(func)


class Problem(Generic[O]):
    """Represents a single problem."""

    def __init__(self, golden: Callable[..., O]) -> None:
        self._golden: Callable[..., O] = golden
        self._test_cases: list[TestCase] = []
        self._golden_test_cases: list[GoldenTestCase] = []

    def add_test_case(self, tc: "TestCase") -> None:
        """Add a test case to the problem.

        The arguments passed to this method will be passed verbatim to the
        golden solution from the class constructor and to the student submission
        which is under test. The student solution will be checked against the
        golden solution; i.e., this method does _not_ produce a test of the
        golden solution.
        """
        self._test_cases.append(tc)

    def add_golden_test_case(self, gtc: "GoldenTestCase") -> None:
        """Add a golden test case to the problem.

        The arguments passed to this method will be passed verbatim to the
        golden solution from the class constructor and to the student submission
        which is under test. Both will be checked against the output; i.e., this
        method produces _both_ a test of the golden solution and of the student
        submission.
        """
        self._golden_test_cases.append(gtc)

    def run_all_golden_tests(self) -> None:
        """Run all tests of the golden solution."""
        for tc in self._golden_test_cases:
            assert tc.check_one(self._golden)
