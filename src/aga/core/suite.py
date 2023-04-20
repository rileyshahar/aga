"""Test Suite for the aga.core module."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
from types import FunctionType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Sequence,
    Tuple,
    TypeVar,
    Iterable,
)
from unittest import TestCase, TestSuite
from unittest.mock import patch

from .parameter import _TestParam, AgaKeywordContainer
from .utils import CaptureOut, initializer, Initializer
from ..config import AgaConfig, AgaTestConfig
from ..score import Prize, ScoredPrize, ScoreInfo, compute_scores
from ..util import text_diff

__all__ = ["TestMetadata", "SubmissionMetadata", "AgaTestCase", "AgaTestSuite"]

Output = TypeVar("Output")

_NEW_LINE = "\n"


@dataclass(frozen=True)
class TestMetadata:
    """Stores metadata about a specific test case."""

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

    @property
    def metadata(self) -> TestMetadata:
        """Get the test's metadata."""
        return self._metadata

    @property
    def test_input(self) -> _TestInputs[Output]:
        """Get the test input."""
        return self._test_input

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
        return self.name

    @property
    def name(self) -> str:
        """Format the name of the test case."""
        return (
            self._test_input.aga_kwargs.name
            or self._metadata.config.name_fmt.format(
                args=self._test_input.param.args_repr(self._metadata.config.name_sep),
                kwargs=self._test_input.param.kwargs_repr(
                    self._metadata.config.name_sep
                ),
                sep=self._test_input.param.sep_repr(self._metadata.config.name_sep),
            )
        )

    @property
    def description(self) -> str | None:
        """Get the problem's description."""
        return self._test_input.aga_kwargs.description


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


class _TestInputs(TestCase, Generic[Output]):
    """A single set of test inputs for a problem.

    These will be run against the golden solution and the function under test; their
    outputs will be compared, and a unittest failure raised if they differ.
    """

    # this tells unittest not to print their default assertion error messages
    longMessage = False

    def __init__(
        self,
        aga_param: _TestParam,
        mock_input: bool,
    ) -> None:
        super().__init__()
        self._mock_input = mock_input
        self._param: _TestParam = aga_param
        self.score_info = ScoreInfo(
            self.aga_kwargs.weight, self.aga_kwargs.value, self.aga_kwargs.extra_credit
        )

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

    @property
    def aga_kwargs(self) -> AgaKeywordContainer:
        """Get the keyword arguments for the test case."""
        return self._param

    @property
    def mock_input(self) -> bool:
        """Get the mock input of the test case."""
        return self._mock_input

    @property
    def description(self) -> str | None:
        """Get the description of the test case."""
        return self.aga_kwargs.description

    @description.setter
    def description(self, desc: str | None) -> None:
        """Set the description of the test case."""
        self.aga_kwargs.description = desc

    @property
    def name(self) -> str | None:
        """Get the description of the test case."""
        return self.aga_kwargs.name

    @name.setter
    def name(self, name: str | None) -> None:
        """Set the description of the test case."""
        self.aga_kwargs.name = name

    def _eval_mock_input(
        self, answer: Callable[..., Output], check_output: bool = False
    ) -> Tuple[str | None, Output]:
        """Evaluate func on the arguments."""
        # deepcopy in case the student submission mutates arguments; we don't want it to
        # mess with our copy of the arguments
        with CaptureOut(check_output) as stdout, patch(
            "builtins.input", generate_custom_input(deepcopy(self.args))
        ):
            result = answer()

        return stdout.value, result

    def _test_mock_input(
        self,
        golden: Callable[..., Output],
        under_test: Callable[..., Output],
        eq_fn: Callable[[_TestInputs[Output], Output, Output, TestMetadata, str], bool],
        metadata: TestMetadata,
    ) -> None:
        golden_stdout, golden_result = self._eval_mock_input(
            golden, metadata.check_stdout
        )

        under_test_stdout, under_test_result = self._eval_mock_input(
            under_test, metadata.check_stdout
        )

        eq_fn(
            self,
            golden_result,
            under_test_result,
            metadata,
            metadata.config.failure_msg,
        )

        self._assert_output_eq(golden_stdout, under_test_stdout, metadata)

    def _eval_regular(
        self, answer: Callable[..., Output], capture_output: bool
    ) -> Tuple[str | None, Output]:
        """Evaluate func on the arguments."""
        with CaptureOut(capture_output) as stdout:
            result = answer(*deepcopy(self.args), **deepcopy(self.kwargs))

        return stdout.value, result

    def _test_regular(
        self,
        golden: Callable[..., Output],
        under_test: Callable[..., Output],
        eq_fn: Callable[[_TestInputs[Output], Output, Output, TestMetadata, str], bool],
        metadata: TestMetadata,
    ) -> None:
        golden_stdout, golden_result = self._eval_regular(golden, metadata.check_stdout)
        under_test_stdout, under_test_result = self._eval_regular(
            under_test, metadata.check_stdout
        )

        eq_fn(
            self,
            golden_result,
            under_test_result,
            metadata,
            metadata.config.failure_msg,
        )

        self._assert_output_eq(golden_stdout, under_test_stdout, metadata)

    def _eval_pipeline(
        self, answer: Callable[..., Output], check_output: bool
    ) -> Tuple[str | None, Sequence[Any]]:
        self.description = ""
        temp_name = initializer.DEFAULT_NEW_INSTANCE_NAME
        if isinstance(answer, (type, FunctionType)):
            temp_name = answer.__name__

        with CaptureOut(check_output) as stdout:
            results = [None]

            if len(self.args) > 0:
                pipeline_processes = self.args

                for process in pipeline_processes:
                    if isinstance(process, Initializer):
                        answer = process(answer)
                        results.append(None)
                        self.description += (
                            f"{process.DEFAULT_NEW_INSTANCE_NAME} = "
                            f"{temp_name}{process}\n"
                        )
                        temp_name = process.DEFAULT_NEW_INSTANCE_NAME
                    else:
                        results.append(process(answer, results[-1]))
                        self.description += f"{temp_name}{process}\n"

        return stdout.value, results

    def _test_pipeline(
        self,
        golden: Callable[..., Output],
        under_test: Callable[..., Output],
        eq_fn: Callable[[_TestInputs[Output], Output, Output, TestMetadata, str], bool],
        metadata: TestMetadata,
    ) -> None:
        golden_stdout, golden_result = self._eval_pipeline(
            golden, metadata.check_stdout
        )
        under_test_stdout, under_test_result = self._eval_pipeline(
            under_test, metadata.check_stdout
        )

        if len(under_test_result) != len(golden_result):
            raise AssertionError(
                f"Expected {len(golden_result)} results, "
                f"but got {len(under_test_result)}"
            )

        for i, (golden_res, under_test_res) in enumerate(
            zip(golden_result[1:], under_test_result[1:])
        ):
            eq_fn(
                self,
                golden_res,
                under_test_res,
                metadata,
                f"The first diff happens in {i}th process (`{self.args[i]}`) "
                f"of the pipeline.\n"
                "The output is {output} and the expected is {expected}\n"
                f"Everything before the {i}th process (`{self.args[i]}`) "
                f"of the pipeline is correct:\n"
                f"{_NEW_LINE.join(map(str, self.args[:i + 1]))}\n\n"
                f"{metadata.config.failure_msg}",
            )

        self._assert_output_eq(golden_stdout, under_test_stdout, metadata)

    def _pick_test_fn(
        self,
    ) -> Callable[
        [
            Callable[..., Output],
            Callable[..., Output],
            Callable[[_TestInputs[Output], Output, Output, TestMetadata, str], bool],
            TestMetadata,
        ],
        None,
    ]:
        if self.mock_input:
            test_fn = self._test_mock_input
        elif self.aga_kwargs.is_pipeline:
            test_fn = self._test_pipeline
        else:
            test_fn = self._test_regular

        return test_fn

    def _pick_eval_fn(
        self,
    ) -> Callable[[Callable[..., Output], bool], Tuple[str, Any]]:
        if self.mock_input:
            test_fn: Any = self._eval_mock_input
        elif self.aga_kwargs.is_pipeline:
            test_fn = self._eval_pipeline
        else:
            test_fn = self._eval_regular

        return test_fn  # type: ignore

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
        if self.aga_kwargs.override_test:
            self.aga_kwargs.override_test(self, golden, under_test)
            return

        if self.aga_kwargs.override_check:
            check = self.aga_kwargs.override_check
        else:
            check = type(self)._assert_eq

        test_fn = self._pick_test_fn()

        test_fn(golden, under_test, check, metadata)

    def _assert_output_eq(
        self, expected: str | None, got: str | None, metadata: TestMetadata
    ) -> None:
        self._assert_eq(
            expected or "",
            got or "",
            metadata,
            metadata.config.stdout_differ_msg,
        )

    def _assert_eq(
        self,
        expected: Any,
        got: Any,
        metadata: TestMetadata,
        msg_format: str,
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
        metadata = TestMetadata(
            hidden=self.aga_kwargs.hidden,
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
        if (
            self.aga_kwargs.expect is not None
            or self.aga_kwargs.expect_stdout is not None
        ):
            if self.aga_kwargs.override_test:

                def dummy_tester(*_: Any, **__: Any) -> Output:
                    # https://github.com/python/mypy/issues/4805 ehh
                    return self.aga_kwargs.expect  # type: ignore

                try:
                    self.aga_kwargs.override_test(
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
                self._default_check(golden)

    def _default_check(self, golden: Callable[..., Output]) -> None:
        """Check that the golden solution is correct."""
        eval_fn = self._pick_eval_fn()
        golden_stdout, golden_output = eval_fn(golden, True)

        # compare output
        if self.aga_kwargs.expect is not None:
            compared_expect_out = self.aga_kwargs.expect
            if self.aga_kwargs.is_pipeline:
                golden_output = golden_output[1:]
                compared_expect_out = list(self.aga_kwargs.expect)

            # if check is overridden, use it
            if self.aga_kwargs.override_check is not None:
                try:
                    self.aga_kwargs.override_check(
                        self, compared_expect_out, golden_output
                    )
                except AssertionError as e:
                    raise AssertionError(
                        "Your solution doesn't pass the overridden check. \n"
                        "Test parameters: \n"
                        f"{self._param}"
                    ) from e
            else:
                self.assertEqual(golden_output, self.aga_kwargs.expect)

        # compare stdout
        if self.aga_kwargs.expect_stdout is not None:
            if isinstance(self.aga_kwargs.expect_stdout, str):
                compared_golden_stdout = golden_stdout
                compared_expected_stdout = self.aga_kwargs.expect_stdout
            elif isinstance(self.aga_kwargs.expect_stdout, Sequence) and isinstance(
                golden_stdout, str
            ):
                compared_golden_stdout = golden_stdout.splitlines()
                compared_expected_stdout = list(self.aga_kwargs.expect_stdout)
            else:
                raise TypeError(
                    "expect_stdout must be a string or a sequence of strings"
                )

            self.assertEqual(compared_expected_stdout, compared_golden_stdout)


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

        for score, case in zip(
            scores, self._test_cases
        ):  # type: float, _TestInputs[Output]
            suite.addTest(case.generate_test_case(golden, under_test, score, config))

        scored_prizes = []
        for score, prize in zip(reversed(scores), reversed(self._prizes)):
            # reverse scores so we get the ones that correspond to the prizes
            scored_prizes.append(
                ScoredPrize(prize=prize, max_score=score)  # type: ignore
            )

        return suite, scored_prizes

    def check_one(self, golden: Callable[..., Output]) -> None:
        """Check the golden solution against all test cases."""
        for case in self._test_cases:
            case.check_one(golden)
