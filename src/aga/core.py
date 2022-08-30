"""The core library functionality."""

from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
from itertools import product
from typing import Any, Callable, Generic, Optional, TypeVar
from unittest import TestCase, TestSuite
from unittest.mock import patch

from .checks import with_captured_stdout
from .config import AgaConfig, AgaTestConfig
from .score import Prize, ScoredPrize, ScoreInfo, compute_scores
from .util import text_diff

Output = TypeVar("Output")


@dataclass(frozen=True)
class TestMetadata:
    """Stores metadata about a specific test case."""

    name: str
    max_score: float
    config: AgaTestConfig
    check_stdout: bool
    mock_input: bool
    hidden: bool = False


@dataclass(frozen=True)
class SubmissionMetadata:
    """Metadata for testing a submission, collected from the frontend.

    Attributes
    ----------
    total_score : float
        The problem's total score.
    time_since-due : timedelta
        The delta _from_ the due date _to_ the submission date, i.e. it's negative if
        the problem was submitted before the due date.
    previous_submissions : int
        The number of previous submissions.

    """

    total_score: float
    time_since_due: timedelta
    previous_submissions: int

    def is_on_time(self) -> bool:
        """Return true of the submission was on time."""
        return self.time_since_due <= timedelta()


class AgaTestCase(TestCase):
    """A `TestCase` which runs a single test of a `Problem`."""

    def __init__(
        self,
        test_input: "_TestInputs[Output]",
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
        self._test_input.check(self._golden, self._under_test, self._metadata)

    # pylint: disable=invalid-name
    # camelCase is required by unittest
    def shortDescription(self) -> str:
        """Dynamically generate the test name.

        This method is called by unittest.
        """
        return self._metadata.name


class AgaTestSuite(TestSuite):
    """A thin wrapper around TestSuite that store a config."""

    def __init__(self, config: AgaConfig, tests: list[AgaTestCase]):
        super().__init__(tests)
        self.config = config


class _TestInputs(TestCase, Generic[Output]):
    """A single set of test inputs for a problem.

    These will be run against the golden solution and the function under test; their
    outputs will be compared, and a unittest failure raised if they differ.
    """

    # this tells unittest not to print their default assertion error messages
    longMessage = False

    def __init__(
        self,
        *args: Any,
        aga_expect: Optional[Output],
        aga_hidden: bool,
        aga_name: Optional[str],
        aga_weight: int,
        aga_value: float,
        aga_mock_input: bool,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self._name = aga_name
        self._hidden = aga_hidden
        self._mock_input = aga_mock_input
        self._expect = aga_expect
        self.score_info = ScoreInfo(aga_weight, aga_value)

        self._args = args
        self._kwargs = kwargs

    def _eval(self, func: Callable[..., Any]) -> Any:
        """Evaluate func on the arguments."""
        # deepcopy in case the student submission mutates arguments; we don't want it to
        # mess with our copy of the arguments
        if self._mock_input:
            with patch("builtins.input", side_effect=[*deepcopy(self._args)]) as _:
                return func()
        else:
            return func(*deepcopy(self._args), **deepcopy(self._kwargs))

    def check(
        self,
        golden: Callable[..., Output],
        under_test: Callable[..., Output],
        metadata: TestMetadata,
    ) -> None:
        """Assert that `golden` and `under_test` give the same output.

        This method relies on `TestCase.assertEqual`, which will raise a unittest error
        if they differ. This means it can be plugged into any unittest TestCase as a
        helper method.
        """
        if metadata.check_stdout:
            golden_stdout, golden_output = self._eval(with_captured_stdout(golden))
            under_test_stdout, under_test_output = self._eval(
                with_captured_stdout(under_test)
            )

            self._assert_eq(
                golden_stdout,
                under_test_stdout,
                metadata,
                metadata.config.stdout_differ_msg,
            )

        else:
            golden_output = self._eval(golden)
            under_test_output = self._eval(under_test)

        self._assert_eq(
            golden_output, under_test_output, metadata, metadata.config.failure_msg
        )

    def _assert_eq(
        self, expected: Output, got: Output, metadata: TestMetadata, msg_format: str
    ) -> None:
        """Assert that expected equals got, formatting `msg_format` if not."""
        # we can only diff strings
        if isinstance(expected, str) and isinstance(got, str):
            diff_explanation = metadata.config.diff_explanation_msg
            diff = text_diff(got, expected)
        else:
            diff_explanation = ""
            diff = ""

        self.assertEqual(
            got,
            expected,
            msg=msg_format.format(
                input=repr(self),
                expected=repr(expected),
                output=repr(got),
                diff_explanation=diff_explanation,
                diff=diff,
            ),
        )

    def generate_test_case(
        self,
        golden: Callable[..., Output],
        under_test: Callable[..., Output],
        score: float,
        config: AgaConfig,
    ) -> AgaTestCase:
        """Generate a TestCase which tests `golden` against `under_test`."""
        name_fmt = config.test.name_fmt
        name_sep = config.test.name_sep

        name = self._name or name_fmt.format(
            args=self._args_repr(name_sep),
            kwargs=self._kwargs_repr(name_sep),
            sep=self._sep(name_sep),
        )
        metadata = TestMetadata(
            name=name,
            hidden=self._hidden,
            config=config.test,
            max_score=score,
            check_stdout=config.problem.check_stdout,
            mock_input=config.problem.mock_input,
        )
        return AgaTestCase(self, golden, under_test, metadata)

    def _args_repr(self, sep: str) -> str:
        return sep.join(repr(x) for x in self._args)

    def _kwargs_repr(self, sep: str) -> str:
        # we use k instead of repr(k) so we don't get quotes around it
        return sep.join(k + "=" + repr(v) for k, v in self._kwargs.items())

    def _sep(self, sep: str) -> str:
        """Return sep if both exist, "" otherwise."""
        assert sep == ","
        return self._args and self._kwargs and sep or ""

    def __repr__(self) -> str:
        args_repr = self._args_repr(",")
        kwargs_repr = self._kwargs_repr(",")
        sep = self._sep(",")

        return args_repr + sep + kwargs_repr

    def check_one(self, golden: Callable[..., Output]) -> None:
        """Check that the golden solution is correct."""
        if self._expect is not None:
            self.assertEqual(self._eval(golden), self._expect)


class _TestInputGroup(Generic[Output]):
    """A group of test cases with shared configuration."""

    def __init__(self, weight: int = 1, value: float = 0.0) -> None:
        self._test_cases: list[_TestInputs[Output]] = []
        self._prizes: list[Prize] = []
        self.score_info = ScoreInfo(weight, value)

    def add_test_case(self, case: _TestInputs[Output]) -> None:
        """Add a test case to the group."""
        self._test_cases.append(case)

    def add_prize(self, prize: Prize) -> None:
        """Add a prize to the group."""
        self._prizes.append(prize)

    def generate_test_suite(
        self,
        golden: Callable[..., Output],
        under_test: Callable[..., Output],
        group_score: float,
        config: AgaConfig,
    ) -> tuple[AgaTestSuite, list[ScoredPrize]]:
        """Generate a test suite from all the test cases for this group."""
        suite = AgaTestSuite(config, [])

        score_infos = [case.score_info for case in self._test_cases] + [
            prize.score_info for prize in self._prizes
        ]
        scores = compute_scores(score_infos, group_score)

        for (score, case) in zip(scores, self._test_cases):
            suite.addTest(case.generate_test_case(golden, under_test, score, config))

        scored_prizes = []
        for (score, prize) in zip(reversed(scores), reversed(self._prizes)):
            # reverse scores so we get the ones that correspond to the prizes
            scored_prizes.append(
                ScoredPrize(prize=prize, max_score=score)  # type: ignore
            )

        return suite, scored_prizes

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
        config: AgaConfig,
        is_script: bool,
    ) -> None:
        self._golden: Callable[..., Output] = golden
        self._name = name
        self._config = config
        self._ungrouped_prizes: list[Prize] = []
        self._ungrouped_tests: list[_TestInputs[Output]] = []
        self._groups: list[_TestInputGroup[Output]] = []
        self.is_script = is_script

    def add_test_case(
        self,
        *args: Any,
        aga_expect: Optional[Output] = None,
        aga_hidden: bool = False,
        aga_name: Optional[str] = None,
        aga_weight: int = 1,
        aga_value: float = 0.0,
        **kwargs: Any,
    ) -> None:
        """Add a test case to the current group.

        Student solutions will be checked against the golden solution; i.e., this method
        does _not_ produce a test of the golden solution.
        """
        case: _TestInputs[Output] = _TestInputs(
            *args,
            aga_expect=aga_expect,
            aga_hidden=aga_hidden,
            aga_name=aga_name,
            aga_weight=aga_weight,
            aga_value=aga_value,
            aga_mock_input=self._config.problem.mock_input,
            **kwargs,
        )
        self._ungrouped_tests.append(case)

    def add_prize(self, prize: Prize) -> None:
        """Add a prize to the current group."""
        self._ungrouped_prizes.append(prize)

    def add_group(self, grp: _TestInputGroup[Output]) -> None:
        """Add a group to the problem."""
        for case in self._ungrouped_tests:
            grp.add_test_case(case)

        for prize in self._ungrouped_prizes:
            grp.add_prize(prize)

        self._groups.append(grp)
        self._ungrouped_tests = []
        self._ungrouped_prizes = []

    def config(self) -> AgaConfig:
        """Get access to the problem's config."""
        return self._config

    def check(self) -> None:
        """Check that the problem is correct.

        Currently, this runs all tests of the golden solution.
        """
        for grp in self._virtual_groups():
            grp.check_one(self._golden)

    def generate_test_suite(
        self, under_test: Callable[..., Output], metadata: "SubmissionMetadata"
    ) -> tuple[AgaTestSuite, list[ScoredPrize]]:
        """Generate a `TestSuite` for the student submitted function.

        Neither the generated test suite nor the body of this function will run golden
        tests; instead, golden test cases are treated as equivalent to ordinary ones. To
        test the golden function, `check` should be used instead.

        Parameters
        ----------
        under_test : Callable[..., Output]
            The student submitted function.
        metadata : SubmissionMetadata
            The submission metadata.

        Returns
        -------
        AgaTestSuite
            A unittest test suite containing one test for each TestInput in this
            problem, checking the result of the problem's golden solution against
            `under_test`.
        list[ScorePrize]
            The prizes for the problem, with scores assigned.
        """
        ret_suite = AgaTestSuite(self._config, [])

        groups = self._virtual_groups()

        score_infos = [grp.score_info for grp in groups]
        scores = compute_scores(score_infos, metadata.total_score)

        ret_prizes = []
        for (score, grp) in zip(scores, groups):
            suite, prizes = grp.generate_test_suite(
                self._golden, under_test, score, self._config
            )
            ret_suite.addTest(suite)
            ret_prizes += prizes

        return ret_suite, ret_prizes

    def name(self) -> str:
        """Get the problem's name."""
        return self._name

    def expected_symbol(self) -> str:
        """Get the name of the symbol that should be tested against."""
        return self._golden.__name__

    def update_config_weak(self, config: AgaConfig) -> None:
        """Update any non-default items in self.config."""
        self._config.update_weak(config)

    def _virtual_groups(self) -> list[_TestInputGroup[Output]]:
        """Get the list of groups, plus the current group under construction.

        We need to do it this way because while the problem is being read we don't know
        the configuration of the last test group yet.
        """
        if self._ungrouped_tests or self._ungrouped_prizes:
            virtual_group: _TestInputGroup[Output] = _TestInputGroup()

            for case in self._ungrouped_tests:
                virtual_group.add_test_case(case)

            for prize in self._ungrouped_prizes:
                virtual_group.add_prize(prize)

            return self._groups + [virtual_group]

        else:
            return self._groups


def problem(
    name: Optional[str] = None,
    script: bool = False,
    check_stdout: Optional[bool] = None,
    mock_input: Optional[bool] = None,
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
    script : bool
        Whether the problem represents a script, as opposed to a function. Implies
        `check_stdout` and `mock_input` unless they are passed explicitly.
    check_stdout : Optional[bool]
        Overrides the `problem.check_stdout` configuration option. If True, check the
        golden solution's stdout against the student submission's for all test cases.
    mock_input : Optional[bool]
        Overrides the `problem.mock_input` configuration option. If True, test cases for
        this problem will be interpreted as mocked outputs of `builtins.input`, rather
        than inputs to the function.

    Returns
    -------
    Callable[[Callable[..., T]], Problem[T]]
        A decorator which turns a golden solution into a problem.
    """
    config = AgaConfig()

    if check_stdout is not None:
        config.problem.check_stdout = check_stdout
        config.problem.check_stdout_overridden = True

    if mock_input is not None:
        config.problem.mock_input = mock_input
        config.problem.mock_input_overridden = True

    def outer(func: Callable[..., Output]) -> Problem[Output]:
        problem_name = name or func.__name__

        if script:
            if check_stdout is None:
                config.problem.check_stdout = True
                config.problem.check_stdout_overridden = True

            if mock_input is None:
                config.problem.mock_input = True
                config.problem.mock_input_overridden = True

        return Problem(func, problem_name, config, script)

    return outer


def _check_reserved_keyword(kwd: str) -> None:
    """Raise an error if `kwd` is reserved."""
    if kwd.startswith("aga_") and kwd not in (
        "aga_expect",
        "aga_hidden",
        "aga_name",
        "aga_weight",
        "aga_value",
    ):
        raise ValueError(
            f'invalid keyword arg "{kwd}" to `test_case`: all keyword args '
            "beginning `aga_` are reserved"
        )


def test_case(
    *args: Any,
    **kwargs: Any,
) -> Callable[[Problem[Output]], Problem[Output]]:
    r"""Declare a specific test case for some problem.

    Parameters
    ----------
    args :
        The arguments to be passed to the functions under test.
    aga_expect : Optional[T]
        If aga_expect is None, the inputs will be tested against the wrapped function,
        the "golden solution" to the problem. If aga_expect is specified, the inputs
        will double as a test _of_ the golden solution; to successfully produce the
        problem grader, the golden solution must return aga_expect from the given input.
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
        prob.add_test_case(
            *args,
            **kwargs,
        )
        return prob

    return outer


def test_cases(
    *args: Iterable[Any],
    aga_product: bool = True,
    **kwargs: Iterable[Any],
) -> Callable[[Problem[Output]], Problem[Output]]:
    r"""Generate many test cases programatically, from generators of inputs.

    Parameters
    ----------
    args :
        Generators for arguments to be passed to the functions under test.
    aga_product : bool
        Whether to take a cartesian product of the generators (creating one test case
        for each set of inputs in the product), or to zip them (iterate through each
        generator in sequence). Default `True`.
    aga_*
        Other `aga_` keywords have their meaning inherited from `test_case`, and are
        applied to each test case generated by this function. Aga_expect is not
        supported.
    kwargs :
        Generators for keyword arguments to be passed to the functions under test. Any
        keyword starting with aga\_ is reserved.

    Returns
    -------
    Callable[[Problem[T]], Problem[T]]
        A decorator which adds the test cases to a problem.
    """

    def outer(prob: Problem[Output]) -> Problem[Output]:
        combinator = product if aga_product else zip

        combined_args = combinator(*args)
        combined_kwargs = combinator(*kwargs.values())

        for curr_args, curr_kwargs in combinator(combined_args, combined_kwargs):
            # we have to reassemble a kwargs dictionary that actually has keys
            final_kwargs = dict(zip(kwargs.keys(), curr_kwargs))

            # i think we have to enumerate all of the arguments to test_case by
            # hand; we can't capture them separately from the test case kwargs
            prob = test_case(
                *curr_args,
                **final_kwargs,
            )(prob)

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

    Returns
    -------
    Callable[[Problem[T]], Problem[T]]
        A decorator which adds the group to a problem.
    """

    def outer(prob: Problem[Output]) -> Problem[Output]:
        prob.add_group(_TestInputGroup(weight, value))
        return prob

    return outer
