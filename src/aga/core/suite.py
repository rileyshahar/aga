"""Test Suite for the aga.core module."""
from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
)
from unittest import TestCase, TestSuite
from unittest.mock import patch

from .parameter import _TestParam
from ..checks import with_captured_stdout
from ..config import AgaConfig, AgaTestConfig
from ..score import Prize, ScoredPrize, ScoreInfo, compute_scores
from ..util import text_diff

__all__ = ["TestMetadata", "SubmissionMetadata", "AgaTestCase", "AgaTestSuite"]

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


def generate_custom_input(input_list: Iterable[str]) -> Callable[[Any], str]:
    """Generate a custom input function for a test case."""
    _iterator = iter(input_list)

    def _custom_input(*args: Any) -> str:
        print(*args)
        return next(_iterator)

    return _custom_input


# pylint: disable=too-many-instance-attributes
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
        aga_expect_stdout: Optional[str | Sequence[str]],
        aga_hidden: bool,
        aga_name: Optional[str],
        aga_weight: int,
        aga_value: float,
        aga_extra_credit: float,
        aga_mock_input: bool,
        aga_override_check: Optional[
            Callable[[_TestInputs[Output], Output, Output], None]
        ],
        aga_override_test: Optional[
            Callable[
                [_TestInputs[Output], Callable[..., Output], Callable[..., Output]],
                None,
            ]
        ],
        aga_param: Optional[_TestParam] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self._name = aga_name
        self._hidden = aga_hidden
        self._mock_input = aga_mock_input
        self._expect = aga_expect
        self._expect_stdout = aga_expect_stdout
        self._override_check = aga_override_check
        self._override_test = aga_override_test
        self.score_info = ScoreInfo(aga_weight, aga_value, aga_extra_credit)

        if aga_param:
            if args or kwargs:
                raise ValueError(
                    "aga_param must be used without any positional or keyword "
                    "argument, but got \n"
                    f"    args: {args}\n"
                    f"    kwargs: {kwargs}"
                )
            self._param: _TestParam = aga_param
        else:
            self._param = _TestParam(*args, **kwargs)

    @property
    def args(self) -> Tuple[Any, ...]:
        """Get the positional arguments for the test case."""
        return self._param.args

    @property
    def kwargs(self) -> Dict[str, Any]:
        """Get the keyword arguments for the test case."""
        return self._param.kwargs

    @property
    def param(self) -> _TestParam:
        """Get the test parameter."""
        return self._param

    def _eval(self, func: Callable[..., Any]) -> Any:
        """Evaluate func on the arguments."""
        # deepcopy in case the student submission mutates arguments; we don't want it to
        # mess with our copy of the arguments
        if self._mock_input:
            with patch(
                "builtins.input", generate_custom_input(deepcopy(self.args))
            ) as _:
                return func()
        else:
            return func(*deepcopy(self.args), **deepcopy(self.kwargs))

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
        if self._override_test:
            self._override_test(self, golden, under_test)
            return

        if self._override_check:
            self._override_check(self, self._eval(golden), self._eval(under_test))
            return

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

        if isinstance(expected, float) and isinstance(got, (float, int)):
            comparator = self.assertAlmostEqual  # type: ignore

        else:
            comparator = self.assertEqual  # type: ignore

        comparator(  # type: ignore
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
            args=self._param.args_repr(name_sep),
            kwargs=self._param.kwargs_repr(name_sep),
            sep=self._param.sep_repr(name_sep),
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

    def __repr__(self) -> str:
        """Get a string representation of the test case."""
        args_repr = self._param.args_repr(",")
        kwargs_repr = self._param.kwargs_repr(",")
        sep = self._param.sep_repr(",")

        return args_repr + sep + kwargs_repr

    def check_one(self, golden: Callable[..., Output]) -> None:
        """Check that the golden solution is correct."""
        if self._expect is not None or self._expect_stdout is not None:
            if self._override_test:

                def dummy_tester(*_: Any, **__: Any) -> Output:
                    # https://github.com/python/mypy/issues/4805 ehh
                    return self._expect  # type: ignore

                try:
                    self._override_test(
                        self,
                        dummy_tester,
                        golden,
                    )
                except AssertionError as e:
                    raise AssertionError(
                        "Your solution doesn't pass the overridden test. \n"
                        "Test parameters: \n"
                        f"{self._param}"
                    ) from e
            else:
                golden_stdout, golden_output = self._eval(
                    with_captured_stdout(golden)
                )  # type: str, Output
                if self._expect is not None:
                    if self._override_check is not None:
                        try:
                            self._override_check(self, self._expect, golden_output)
                        except AssertionError as e:
                            raise AssertionError(
                                "Your solution doesn't pass the overridden check. \n"
                                "Test parameters: \n"
                                f"{self._param}"
                            ) from e
                    else:
                        self.assertEqual(golden_output, self._expect)

                if self._expect_stdout is not None:
                    if isinstance(self._expect_stdout, str):
                        self.assertEqual(golden_stdout, self._expect_stdout)
                    elif isinstance(self._expect_stdout, Sequence):
                        self.assertEqual(
                            golden_stdout.splitlines(), list(self._expect_stdout)
                        )


class _TestInputGroup(Generic[Output]):
    """A group of test cases with shared configuration."""

    def __init__(
        self, weight: int = 1, value: float = 0.0, extra_credit: float = 0.0
    ) -> None:
        self._test_cases: list[_TestInputs[Output]] = []
        self._prizes: list[Prize] = []
        self.score_info = ScoreInfo(weight, value, extra_credit)

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

        for (score, case) in zip(
            scores, self._test_cases
        ):  # type: float, _TestInputs[Output]
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
