"""Methods for running tests.

The main work of this module is to turn a test suite, generated by the core module, into
an `AgaProblemOutput`, which contains data related to test success or failure. It
provides the `run` method, which does so.

For convenience, it also provides the `load_and_run` method, which loads a student
submission and then runs it.
"""

from dataclasses import dataclass
from typing import Any, Optional
from unittest import TestResult

from .config import AgaConfig
from .core import AgaTestCase, AgaTestSuite, Output, Problem
from .loader import (
    NoMatchingSymbol,
    SubmissionSyntaxError,
    TooManyMatchingSymbols,
    load_symbol_from_path,
)
from .util import limited_traceback


@dataclass
class AgaTestCaseOutput:
    """Stores information about a completed test case.

    Attributes
    ----------
    score : float
        The test's score.
    max_score : float
        The max score for the test.
    name : str
        The test's name.
    output : Optional[str]
        Human-readable text output of the test. Some frontends distinguish between no
        output and empty output, i.e. in terms of showing UI elements.
    hidden : bool
        The test's visibility.
    """

    score: float
    max_score: float
    name: str
    output: Optional[str] = None
    hidden: bool = False


@dataclass
class AgaProblemOutput:
    """Stores information about a completed problem.

    Attributes
    ----------
    score : float
        The total score for the problem. We currently do not track max score,
        but instead expect frontends to do so.
    tests : list[AgaTestCaseOutput]
        The test cases for the problem.
    output : str
        Human-readable text output of the problem.
    """

    tests: list[AgaTestCaseOutput]
    score: float
    output: str


class _AgaTestResult(TestResult):
    """A custom `TestResult` that constructs the gradescope json object for the test.

    This is _not_ safe to be used in place of an arbitrary TestResult. This is because
    it relies on specific methods of the `AgaTestCase` class. It should only be used
    with TestSuites that we _know_ only containt `AgaTestCase`s.
    """

    def __init__(self, config: AgaConfig, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._tests: list[AgaTestCaseOutput] = []
        self._output_msgs: list[str] = []
        self._config = config

    @staticmethod
    def _test_data(test: AgaTestCase) -> AgaTestCaseOutput:
        """Construct the test data for a successful test, with _no_ output."""
        metadata = test.metadata()

        return AgaTestCaseOutput(
            max_score=metadata.max_score,
            name=metadata.name,
            score=metadata.max_score,
            hidden=metadata.hidden,
        )

    def _fail_data(self, test: AgaTestCase, err) -> AgaTestCaseOutput:  # type: ignore
        """Construct the test json schema for a failure."""
        data = self._test_data(test)
        data.output = str(err[1])
        data.score = 0.0

        return data

    def _err_data(self, test: AgaTestCase, err) -> AgaTestCaseOutput:  # type: ignore
        """Construct the test json schema for an error."""
        data = self._test_data(test)
        data.output = test.metadata().error_msg.format(
            type=err[0].__name__,
            message=err[1],
            traceback=limited_traceback(err[2]),
        )
        data.score = 0.0

        return data

    # lots of type: ignores because these methods all restrict the input TestCase type

    def addError(self, test: AgaTestCase, err) -> None:  # type: ignore
        """Add an error."""
        super().addError(test, err)
        self._tests.append(self._err_data(test, err))

    def addFailure(self, test: AgaTestCase, err) -> None:  # type: ignore
        """Add a failure."""
        super().addFailure(test, err)
        self._tests.append(self._fail_data(test, err))

    def addSuccess(self, test: AgaTestCase) -> None:  # type: ignore[override]
        """Add a success."""
        super().addSuccess(test)
        self._tests.append(self._test_data(test))

    def _score(self) -> float:
        """Get the total score."""
        return sum(t.score for t in self._tests)

    def _output(self) -> str:
        """Get the current output string.

        Generally, `build_output` should be called once, and then this method used for
        subsequent gets.
        """
        return "\n\n".join(self._output_msgs)

    def _build_output(self) -> str:
        """Build the main output string."""
        config = self._config.submission

        failed_tests = [t for t in self._tests if t.score < t.max_score]
        if failed_tests:
            # add failed test message
            self._output_msgs.append(config.failed_tests_msg)

            if any(t.hidden for t in failed_tests):
                # add hidden test message
                self._output_msgs.append(config.failed_hidden_tests_msg)

        else:
            self._output_msgs.append(config.no_failed_tests_msg)

        return self._output()

    def build(self) -> AgaProblemOutput:
        """Get the completed output data."""
        return AgaProblemOutput(
            tests=self._tests, score=self._score(), output=self._build_output()
        )


def run(suite: AgaTestSuite) -> AgaProblemOutput:
    """Run the suite, returning the output."""
    return suite.run(_AgaTestResult(suite.config)).build()  # type: ignore


def load_and_run(
    problem: Problem[Output], path: str, total_points: float
) -> AgaProblemOutput:
    """Load the submission and then run the suite, returning the output.

    The path can be either a directory, which will be searched without recurring into
    subdirctories, or a single file. This method handles errors from missing or invalid
    submissions.
    """
    try:
        under_test = load_symbol_from_path(path, problem.expected_symbol())
    except SubmissionSyntaxError as err:
        return AgaProblemOutput(
            output=_submission_syntax_error_msg(
                err.__cause__, problem.config()  # type: ignore
            ),
            tests=[],
            score=0.0,
        )
    except NoMatchingSymbol:
        return AgaProblemOutput(
            output=_no_matches_error_msg(problem),
            tests=[],
            score=0.0,
        )
    except TooManyMatchingSymbols:
        return AgaProblemOutput(
            output=_too_many_matches_error_msg(problem),
            tests=[],
            score=0.0,
        )

    suite = problem.generate_test_suite(under_test, total_points)
    return run(suite)


def _submission_syntax_error_msg(cause: SyntaxError, config: AgaConfig) -> str:
    return config.submission.import_error_msg.format(message=str(cause))


def _no_matches_error_msg(problem: Problem[Output]) -> str:
    return problem.config().submission.no_match_msg.format(
        name=problem.expected_symbol()
    )


def _too_many_matches_error_msg(problem: Problem[Output]) -> str:
    return problem.config().submission.too_many_matches_msg.format(
        name=problem.expected_symbol()
    )
