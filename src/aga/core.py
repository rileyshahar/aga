"""The core library functionality.

There are mypy "type: ignore" comments scattered throughout this file. This is because
typing *args and **kwargs is quite difficult. There might be a way to do this, but I'm
not sure how, and it seemed much easier to just ignore them.
"""

from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, TypeVar
from unittest import TestCase, TestSuite

from .score import ScoreInfo, compute_scores

Output = TypeVar("Output")


@dataclass(frozen=True)
class TestMetadata:
    """Stores metadata about a specific class.

    Attributes
    ----------
    name : str
        The test's name.
    hidden : bool
        Whether the test should be hidden.
    max_score : float
        The test's max score.
    """

    name: str
    max_score: float
    hidden: bool = False


class AgaTestCase(TestCase):
    """A `TestCase` which runs a single test of a `Problem`."""

    def __init__(
        self,
        test_input: "_TestInputs",
        golden: Callable[..., Output],
        under_test: Callable[..., Output],
        metadata: TestMetadata,
    ) -> None:
        super().__init__()
        self._test_input = test_input
        self._golden = golden
        self._under_test = under_test
        self._metadata = metadata

    def metadata(self) -> TestMetadata:
        """Get the test's metadata."""
        return self._metadata

    # pylint: disable=invalid-name
    # camelCase is required by unittest
    def runTest(self) -> None:
        """Run the test case."""
        self._test_input.check(self._golden, self._under_test)

    # pylint: disable=invalid-name
    # camelCase is required by unittest
    def shortDescription(self) -> str:
        """Dynamically generate the test name.

        This method is called by unittest.
        """
        return self.metadata().name


class _TestInputs(TestCase):
    """A single set of test inputs for a problem.

    These will be run against the golden solution and the function under test; their
    outputs will be compared, and a unittest failure raised if they differ.
    """

    def __init__(  # type: ignore
        self,
        *args,
        aga_hidden: bool,
        aga_name: Optional[str],
        aga_weight: int,
        aga_value: float,
        **kwargs,
    ) -> None:
        super().__init__()
        self._name = aga_name
        self._hidden = aga_hidden
        self.score_info = ScoreInfo(aga_weight, aga_value)

        self._args = args  # type: ignore
        self._kwargs = kwargs  # type: ignore

    def _eval(self, func: Callable[..., Output]) -> Output:
        """Evaluate func on the arguments."""
        return func(*self._args, **self._kwargs)

    def check(
        self, golden: Callable[..., Output], under_test: Callable[..., Output]
    ) -> None:
        """Assert that `golden` and `under_test` give the same output.

        This method relies on `TestCase.assertEqual`, which will raise a unittest error
        if they differ. This means it can be plugged into any unittest TestCase as a
        helper method.
        """
        golden_output = self._eval(golden)
        under_test_output = self._eval(under_test)

        self.assertEqual(
            golden_output,
            under_test_output,
            msg=(
                f"Checked with {repr(self)}. Expected {repr(golden_output)}. "
                f"Got {repr(under_test_output)} instead."
            ),
        )

    def generate_test_case(
        self,
        golden: Callable[..., Output],
        under_test: Callable[..., Output],
        score: float,
    ) -> AgaTestCase:
        """Generate a TestCase which tests `golden` against `under_test`."""
        metadata = TestMetadata(
            name=self._name or f"Test on {repr(self)}",
            hidden=self._hidden,
            max_score=score,
        )
        return AgaTestCase(self, golden, under_test, metadata)

    def _args_repr(self) -> str:
        return ",".join(repr(x) for x in self._args)

    def _kwargs_repr(self) -> str:
        # we use k instead of repr(k) so we don't get quotes around it
        return ",".join(k + "=" + repr(v) for k, v in self._kwargs.items())

    @staticmethod
    def _repr_sep(args_repr: str, kwargs_repr: str) -> str:
        """Return ',' if both exist, '' otherwise."""
        return args_repr and kwargs_repr and "," or ""

    def __repr__(self) -> str:
        args_repr = self._args_repr()
        kwargs_repr = self._kwargs_repr()
        sep = self._repr_sep(args_repr, kwargs_repr)

        return args_repr + sep + kwargs_repr

    def check_one(self, golden: Callable[..., Output]) -> None:
        """Check that the golden solution is correct.

        This should be implemented by subclasses which expose this functionality.
        """


class _GoldenTestInputs(_TestInputs):
    """A set of test inputs which also contains an expected output.

    This will be treated as a `TestInput` when the autograder is built, but provides
    additional methods to verify a golden solution against the expected output, for
    testing the accuracy of the golden solution against known outputs.
    """

    def __init__(self, output: Output, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._output = output

    def check_one(self, golden: Callable[..., Output]) -> None:
        """Assert that `golden`'s output matches the golden output."""
        self.assertEqual(self._eval(golden), self._output)


class _TestInputGroup:
    """A group of test cases with shared configuration."""

    def __init__(self, weight: int = 1, value: float = 0.0) -> None:
        self._test_cases: list[_TestInputs] = []
        self.score_info = ScoreInfo(weight, value)

    def add_test_case(self, case: _TestInputs) -> None:
        """Add a test case to the group."""
        self._test_cases.append(case)

    def generate_test_suite(
        self,
        golden: Callable[..., Output],
        under_test: Callable[..., Output],
        group_score: float,
    ) -> TestSuite:
        """Generate a test suite from all the test cases for this group."""
        suite = TestSuite([])

        score_infos = [case.score_info for case in self._test_cases]
        scores = compute_scores(score_infos, group_score)

        for (score, case) in zip(scores, self._test_cases):
            suite.addTest(case.generate_test_case(golden, under_test, score))

        return suite

    def check_one(self, golden: Callable[..., Output]) -> None:
        """Check the golden solution against all test cases."""
        for case in self._test_cases:
            case.check_one(golden)


class Problem(Generic[Output]):
    """Stores tests for a single problem."""

    def __init__(
        self,
        golden: Callable[..., Output],
        name: str,
    ) -> None:
        self._golden: Callable[..., Output] = golden
        self._name = name
        self._ungrouped_tests: list[_TestInputs] = []
        self._groups: list[_TestInputGroup] = []

    def add_test_case(self, case: _TestInputs) -> None:
        """Add a test case to the problem.

        Student solutions will be checked against the golden solution; i.e., this method
        does _not_ produce a test of the golden solution.
        """
        self._ungrouped_tests.append(case)

    def add_group(self, grp: _TestInputGroup) -> None:
        """Add a group to the problem."""
        for case in self._ungrouped_tests:
            grp.add_test_case(case)

        self._groups.append(grp)
        self._ungrouped_tests = []

    def check(self) -> None:
        """Check that the problem is correct.

        Currently, this runs all tests of the golden solution.
        """
        for grp in self._virtual_groups():
            grp.check_one(self._golden)

    def generate_test_suite(
        self, under_test: Callable[..., Output], total_score: float
    ) -> TestSuite:
        """Generate a `TestSuite` for the student submitted function.

        Neither the generated test suite nor the body of this function will run golden
        tests; instead, golden test cases are treated as equivalent to ordinary ones. To
        test the golden function, `check` should be used instead.

        Parameters
        ----------
        under_test : Callable[..., Output]
            The student submitted function.
        total_score : float
            The total score for the problem.

        Returns
        -------
        TestSuite
            A unittest test suite containing one test for each TestInput in this
            problem, checking the result of the problem's golden solution against
            `under_test`.
        """
        suite = TestSuite([])

        groups = self._virtual_groups()

        score_infos = [grp.score_info for grp in groups]
        scores = compute_scores(score_infos, total_score)

        for (score, grp) in zip(scores, groups):
            suite.addTest(grp.generate_test_suite(self._golden, under_test, score))

        return suite

    def name(self) -> str:
        """Get the problem's name."""
        return self._name

    def expected_symbol(self) -> str:
        """Get the name of the symbol that should be tested against."""
        return self._golden.__name__

    def _virtual_groups(self) -> list[_TestInputGroup]:
        """Get the list of groups, plus the current group under construction.

        We need to do it this way because while the problem is being read we don't know
        the configuration of the last test group yet.
        """
        virtual_group = _TestInputGroup()

        for case in self._ungrouped_tests:
            virtual_group.add_test_case(case)

        return self._groups + [virtual_group]


def problem(
    name: Optional[str] = None,
) -> Callable[[Callable[..., Output]], Problem[Output]]:
    """Declare a function as the golden solution to a problem.

    This method should decorate a function which is known to produce the correct
    outputs, which we refer to as the "golden solution". It also provides facilities
    for testing that solution, via golden test cases, constructed by passing the
    output argument to the test_case decorator.

    Parameters
    ----------
    name : Optional[str]
        The problem's name. If None (the default), the wrapped function's name will be
        used.

    Returns
    -------
    Callable[[Callable[..., T]], Problem[T]]
        A decorator which turns a golden solution into a problem.
    """

    def outer(func: Callable[..., Output]) -> Problem[Output]:
        problem_name = name or func.__name__

        return Problem(func, problem_name)

    return outer


def _check_reserved_keyword(kwd: str) -> None:
    """Raise an error if `kwd` is reserved."""
    if kwd.startswith("aga_"):
        raise ValueError(
            f'invalid keyword arg "{kwd}" to `test_case`: all keyword args '
            "beginning `aga_` are reserved"
        )


def test_case(  # type: ignore
    *args,
    aga_output: Optional[Any] = None,
    aga_hidden: bool = False,
    aga_name: Optional[str] = None,
    aga_weight: int = 1,
    aga_value: float = 0.0,
    **kwargs,
) -> Callable[[Problem[Output]], Problem[Output]]:
    r"""Declare a specific test case for some problem.

    Parameters
    ----------
    args :
        The arguments to be passed to the functions under test.
    aga_output : Optional[T]
        If aga_output is None, the inputs will be tested against the wrapped function,
        the "golden solution" to the problem. If aga_output is specified, the inputs
        will double as a test _of_ the golden solution; to successfully produce the
        problem grader, the golden solution must return aga_output from the given input.
    aga_hidden : bool
        If True, hide the problem from students on supported frontends.
    aga_name : Optional[str]
        The test case's name. If `None`, defaults to "Test {inputs}", where {inputs} is
        a comma-separated list of args and kwargs.
    aga_weight : int
        The test case's relative weight to the group's score. See :ref:`Determining
        Score` for details.
    aga_value : int
        The test case's absolute score. See :ref:`Determining Score` for details.
    kwargs :
        Keyword arguments to be passed to the functions under test. Any keyword starting
        with aga\_ is reserved.

    Returns
    -------
    Callable[[Problem[T]], Problem[T]]
        A decorator which adds the test case to a problem.
    """
    for kwd, _ in kwargs.items():
        _check_reserved_keyword(kwd)

    def outer(prob: Problem[Output]) -> Problem[Output]:
        if aga_output is not None:
            case: _TestInputs = _GoldenTestInputs(
                aga_output,
                *args,
                aga_hidden=aga_hidden,
                aga_name=aga_name,
                aga_weight=aga_weight,
                aga_value=aga_value,
                **kwargs,
            )

        else:
            case = _TestInputs(
                *args,
                aga_hidden=aga_hidden,
                aga_name=aga_name,
                aga_weight=aga_weight,
                aga_value=aga_value,
                **kwargs,
            )

        prob.add_test_case(case)
        return prob

    return outer


def group(
    weight: int = 1, value: float = 0.0
) -> Callable[[Problem[Output]], Problem[Output]]:
    """Declare a group of problems.

    Parameters
    ----------
    weight : int
        The group's relative weight to the problem's score. See :ref:`Determining Score`
        for details.
    value : int
        The group's absolute score. See :ref:`Determining Score` for details.
    """

    def outer(prob: Problem[Output]) -> Problem[Output]:
        prob.add_group(_TestInputGroup(weight, value))
        return prob

    return outer
