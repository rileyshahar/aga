"""Methods for running tests.

The main work of this module is to turn a test suite, generated by the core module, into
an `ProblemOutput`, which contains data related to test success or failure. It
provides the `run` method, which does so.

For convenience, it also provides the `load_and_run` method, which loads a student
submission and then runs it.
"""

from dataclasses import dataclass
from typing import Any, Literal, Optional, TypeVar
from unittest import TestResult

from .config import AgaConfig
from .core import AgaTestCase, AgaTestSuite, Problem, SubmissionMetadata
from .core.problem import ProblemOutputType, ProblemParamSpec
from .loader import (
    MultipleScripts,
    NoMatchingSymbol,
    NoScript,
    SubmissionSyntaxError,
    TooManyMatchingSymbols,
    load_script_from_path,
    load_symbol_from_path,
)
from .score import ScoredPrize
from .util import limited_traceback

Output = TypeVar("Output")


@dataclass
class TcOutput:
    """Stores information about a completed test case.

    Attributes
    ----------
    score : float
        The test's score.
    max_score : float
        The max score for the test.
    name : str
        The test's name.
    status : Literal["passed", "failed"]
        Whether the test passed or failed.
    description : Optional[str]
        Human-readable text description of the test. Some frontends distinguish
        between no output and empty output, i.e. in terms of showing UI elements.
    error_description: Optional[str]
        Human-readable error description of the test.
    hidden : bool
        The test's visibility.
    """

    score: float
    max_score: float
    name: str
    status: Literal["passed", "failed"]
    hidden: bool = False
    description: Optional[str] = None
    error_description: Optional[str] = None

    @staticmethod
    def format_error_description(error: str) -> str:
        """Format an error description."""
        return "Error: \n" f"{error}\n\n"

    @staticmethod
    def format_description(desc: str) -> str:
        """Format a description."""
        return f"{desc}\n\n"

    @staticmethod
    def format_rich_output(
        description: Optional[str] = None, error_description: Optional[str] = None
    ) -> str:
        """Format a rich output."""
        res = ""
        if description:
            res += TcOutput.format_description(description)
        if error_description:
            res += TcOutput.format_error_description(error_description)

        return res.strip()

    @property
    def rich_output(self) -> str:
        """Output of all the descriptions."""
        return TcOutput.format_rich_output(self.description, self.error_description)

    def is_correct(self) -> bool:
        """Check whether the problem received full credit."""
        return self.status == "passed"


@dataclass
class ProblemOutput:
    """Stores information about a completed problem.

    Attributes
    ----------
    score : float
        The total score for the problem. We currently do not track max score,
        but instead expect frontends to do so.
    tests : list[TcOutput]
        The test cases for the problem.
    output : str
        Human-readable text output of the problem.
    """

    tests: list[TcOutput]
    score: float
    output: str


class _AgaTestResult(TestResult):
    """A custom `TestResult` that constructs the gradescope json object for the test.

    This is _not_ safe to be used in place of an arbitrary TestResult. This is because
    it relies on specific methods of the `AgaTestCase` class. It should only be used
    with TestSuites that we _know_ only containt `AgaTestCase`s.
    """

    def __init__(
        self,
        config: AgaConfig,
        prizes: list[ScoredPrize],
        metadata: SubmissionMetadata,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._tests: list[TcOutput] = []
        self._output_msgs: list[str] = []
        self._config = config
        self._prizes = prizes
        self._metadata = metadata

    @staticmethod
    def _test_data(test: AgaTestCase) -> TcOutput:
        """Construct the test data for a successful test, with _no_ output."""
        metadata = test.metadata

        return TcOutput(
            name=test.name,
            description=test.description,
            status="passed",
            max_score=metadata.max_score,
            score=metadata.max_score,
            hidden=metadata.hidden,
        )

    def _fail_data(self, test: AgaTestCase, err) -> TcOutput:  # type: ignore
        """Construct the test data for a failure."""
        data = self._test_data(test)
        data.error_description = str(err[1])
        data.score = 0.0
        data.status = "failed"

        return data

    def _err_data(self, test: AgaTestCase, err) -> TcOutput:  # type: ignore
        """Construct the test data for an error."""
        data = self._test_data(test)
        data.error_description = test.metadata.config.error_msg.format(
            type=err[0].__name__,
            message=err[1],
            traceback=limited_traceback(err[2]),
        )
        data.score = 0.0
        data.status = "failed"

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

    def _add_prizes(self) -> None:
        prize_tests = []

        for prize in self._prizes:
            # mypy bug (https://github.com/python/mypy/issues/5485, fixed on main)
            scalar, message = prize.prize.criteria(  # type: ignore
                self._tests, self._metadata
            )
            score = scalar * prize.max_score
            status = "failed" if score == 0.0 else "passed"
            prize_out = TcOutput(
                score=score,
                max_score=prize.max_score,
                name=prize.prize.name,
                description=message,
                status=status,
                hidden=prize.prize.hidden,
            )

            # don't append to self._tests immediately so the next prizes don't see this
            # one
            prize_tests.append(prize_out)

        self._tests += prize_tests

    def _build_output(self) -> str:
        """Build the main output string."""
        config = self._config.submission

        failed_tests = [t for t in self._tests if not t.is_correct()]
        if failed_tests:
            # add failed test message
            self._output_msgs.append(config.failed_tests_msg)

            if any(t.hidden for t in failed_tests):
                # add hidden test message
                self._output_msgs.append(config.failed_hidden_tests_msg)

        else:
            self._output_msgs.append(config.no_failed_tests_msg)

        return self._output()

    def build(self) -> ProblemOutput:
        """Get the completed output data."""
        output = self._build_output()
        # we run this after so the tests failed message gets built without taking prizes
        # into account
        self._add_prizes()

        return ProblemOutput(tests=self._tests, score=self._score(), output=output)


def _run(
    suite: AgaTestSuite, prizes: list[ScoredPrize], metadata: SubmissionMetadata
) -> ProblemOutput:
    """Run the suite, returning the output."""
    return suite.run(  # type: ignore
        _AgaTestResult(suite.config, prizes, metadata)
    ).build()


def load_and_run(
    problem: Problem[ProblemParamSpec, ProblemOutputType],
    path: str,
    metadata: SubmissionMetadata,
) -> ProblemOutput:
    """Load the submission and then run the suite, returning the output.

    The path can be either a directory, which will be searched without recurring into
    subdirectories, or a single file. This method handles errors from missing or invalid
    submissions.
    """
    try:
        if not problem.is_script:
            under_test = load_symbol_from_path(path, problem.expected_symbol())
        else:
            under_test = load_script_from_path(path)
    except SubmissionSyntaxError as err:
        return ProblemOutput(
            output=_submission_syntax_error_msg(
                err.__cause__, problem.config()  # type: ignore
            ),
            tests=[],
            score=0.0,
        )
    except NoMatchingSymbol:
        return ProblemOutput(
            output=_no_matches_error_msg(problem),
            tests=[],
            score=0.0,
        )
    except TooManyMatchingSymbols:
        return ProblemOutput(
            output=_too_many_matches_error_msg(problem),
            tests=[],
            score=0.0,
        )
    except NoScript:
        return ProblemOutput(
            output=_no_script_error_msg(problem),
            tests=[],
            score=0.0,
        )
    except MultipleScripts:
        return ProblemOutput(
            output=_multiple_scripts_error_msg(problem),
            tests=[],
            score=0.0,
        )

    suite, prizes = problem.generate_test_suite(under_test, metadata)
    return _run(suite, prizes, metadata)


def _submission_syntax_error_msg(cause: SyntaxError, config: AgaConfig) -> str:
    return config.loader.import_error_msg.format(message=str(cause))


def _no_matches_error_msg(problem: Problem[ProblemParamSpec, ProblemOutputType]) -> str:
    return problem.config().loader.no_match_msg.format(name=problem.expected_symbol())


def _too_many_matches_error_msg(
    problem: Problem[ProblemParamSpec, ProblemOutputType]
) -> str:
    return problem.config().loader.too_many_matches_msg.format(
        name=problem.expected_symbol()
    )


def _no_script_error_msg(problem: Problem[ProblemParamSpec, ProblemOutputType]) -> str:
    return problem.config().loader.no_script_error_msg


def _multiple_scripts_error_msg(
    problem: Problem[ProblemParamSpec, ProblemOutputType]
) -> str:
    return problem.config().loader.multiple_scripts_error_msg
