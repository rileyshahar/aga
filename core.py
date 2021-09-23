from typing import Any, Callable, Generic, Optional, TypeVar
from unittest import TestCase, TestSuite, defaultTestLoader

O = TypeVar("O")


class _AutograderTestCase(TestCase):
    """A `TestCase` which runs a single test of a `Problem`."""

    def __init__(
        self,
        test_input: "_TestInputs",
        golden: Callable[..., O],
        under_test: Callable[..., O],
    ) -> None:
        super().__init__()
        self._test_input = test_input
        self._golden = golden
        self._under_test = under_test

    def runTest(self):
        """Run the test case."""
        self._test_input.check(self._golden, self._under_test)


class _TestInputs(TestCase):
    """A single set of test inputs for a problem.

    These will be run against the golden solution and the function under test;
    their outputs will be compared, and a unittest failure raised if they
    differ.
    """

    def __init__(self, *args, **kwargs) -> None:

        super().__init__()
        self._args: tuple = args
        self._kwargs: dict = kwargs

    def _eval(self, func: Callable[..., O]) -> O:
        """Evaluate func on the arguments."""
        return func(*self._args, **self._kwargs)

    def check(self, golden: Callable[..., O], under_test: Callable[..., O]) -> None:
        """Assert that `golden` and `under_test` give the same output.

        This method relies on `TestCase.assertEqual`, which will raise a
        unittest error if they differ. This means it can be plugged into any
        unittest TestCase as a helper method.
        """
        self.assertEqual(self._eval(golden), self._eval(under_test))

    def generate_test_case(
        self, golden: Callable[..., O], under_test: Callable[..., O]
    ) -> _AutograderTestCase:
        """Generate an `AutograderTestCase` which tests `golden` against `under_test`."""
        return _AutograderTestCase(self, golden, under_test)


class _GoldenTestInputs(_TestInputs, TestCase):
    """A set of test inputs which also contains an expected output.

    This will be treated as a `TestInput` when the autograder is built, but
    provides additional methods to verify a golden solution against the expected
    output, for testing the accuracy of the golden solution against known
    outputs.
    """

    def __init__(self, output: O, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)
        self._output = output

    def check_one(self, under_test: Callable[..., O]) -> None:
        """Assert that `under_test`'s output matches the golden output."""
        self.assertEqual(self._eval(under_test), self._output)


class Problem(Generic[O]):
    """Represents a single problem."""

    def __init__(self, golden: Callable[..., O]) -> None:
        self._golden: Callable[..., O] = golden
        self._test_cases: list[_TestInputs] = []
        self._golden_test_cases: list[_GoldenTestInputs] = []

    def add_test_case(self, tc: _TestInputs) -> None:
        """Add a test case to the problem.

        Student solutions will be checked against the golden solution; i.e.,
        this method does _not_ produce a test of the golden solution.
        """
        self._test_cases.append(tc)

    def add_golden_test_case(self, gtc: _GoldenTestInputs) -> None:
        """Add a golden test case to the problem.

        Student solutions will be checked against the golden solution, and both
        against the output pasted to the GoldenTestInputs constructor; i.e., this
        method _does_ produce a test of the golden solution.
        """
        self._golden_test_cases.append(gtc)

    def run_golden_tests(self) -> None:
        """Run all tests of the golden solution."""
        for tc in self._golden_test_cases:
            tc.check_one(self._golden)

    def generate_test_suite(self, under_test: Callable[..., O]) -> TestSuite:
        """Generate a `TestSuite` for the student submitted function."""
        ts = TestSuite([])

        for tc in self._test_cases:
            ts.addTest(tc.generate_test_case(self._golden, under_test))

        for tc in self._golden_test_cases:
            ts.addTest(tc.generate_test_case(self._golden, under_test))

        return ts


def problem(func: Callable[..., O]) -> Problem[O]:
    """Declare a function as the golden solution to a problem.

    This method should decorate a function which is known to produce the correct
    outputs, which we refer to as the "golden solution". A number of decorators
    are available for both pre- and post-processing of the golden solution and
    the `Problem` created by this decorator.
    """
    return Problem(func)


def test_case(
    *args, output: Optional[Any] = None, **kwargs
) -> Callable[[Problem[O]], Problem[O]]:
    """Declare a specific test case for some problem.

    If `output` is None, the inputs will be tested against the wrapped function,
    the "golden solution" to the problem. If `output` is specified, the inputs
    will double as a test _of_ the golden solution; to successfully produce the
    problem grader, the golden solution must return output from the given input.

    The autograder assumes all golden solutions are correct. A golden test case,
    declared by setting `output`, will _not_ be tested in the autograder itself;
    instead, it should be used for unit testing the golden solution in the dev
    environment. The `Problem` class provides a `run_golden_tests` method which
    asserts that the golden solution returns the correct output for each test
    case with a provided output.
    """

    def outer(problem: Problem[O]) -> Problem[O]:
        if output is not None:
            problem.add_golden_test_case(_GoldenTestInputs(output, *args, *kwargs))
            return problem

        else:
            problem.add_test_case(_TestInputs(*args, **kwargs))
            return problem

    return outer
