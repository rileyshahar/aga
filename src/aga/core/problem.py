"""Problem and utilities."""
from __future__ import annotations

from typing import (
    Callable,
    Generic,
    Optional,
    TYPE_CHECKING,
    TypeVar,
    ParamSpec,
)

from .suite import _TestInputs, _TestInputGroup, AgaTestSuite, SubmissionMetadata
from ..config import AgaConfig
from ..score import Prize, ScoredPrize, compute_scores


# pylint: disable=invalid-name
ProblemParamSpec = ParamSpec("ProblemParamSpec")
ProblemOutputType = TypeVar("ProblemOutputType")


if TYPE_CHECKING:
    from .parameter import _TestParam

__all__ = ["Problem", "problem", "group", "ProblemOutputType", "ProblemParamSpec"]


class Problem(Generic[ProblemParamSpec, ProblemOutputType]):
    """Stores tests for a single problem."""

    def __init__(
        self,
        golden: Callable[ProblemParamSpec, ProblemOutputType],
        name: str,
        config: AgaConfig,
        is_script: bool,
    ) -> None:
        self._golden: Callable[..., ProblemOutputType] = golden
        self._name = name
        self._config = config
        self._ungrouped_prizes: list[Prize] = []
        self._ungrouped_tests: list[_TestInputs[ProblemOutputType]] = []
        self._groups: list[_TestInputGroup[ProblemOutputType]] = []
        self.is_script = is_script

    def add_test_case(self, param: _TestParam) -> None:
        """Add a test case to the current group.

        Student solutions will be checked against the golden solution; i.e., this method
        does _not_ produce a test of the golden solution.
        """
        case: _TestInputs[ProblemOutputType] = _TestInputs(
            param, mock_input=self._config.problem.mock_input
        )
        self._ungrouped_tests.append(case)

    def add_prize(self, prize: Prize) -> None:
        """Add a prize to the current group."""
        self._ungrouped_prizes.append(prize)

    def add_group(self, grp: _TestInputGroup[ProblemOutputType]) -> None:
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
        self,
        under_test: Callable[ProblemParamSpec, ProblemOutputType],
        metadata: SubmissionMetadata,
    ) -> tuple[AgaTestSuite, list[ScoredPrize]]:
        """Generate a `TestSuite` for the student submitted function.

        Neither the generated test suite nor the body of this function will run golden
        tests; instead, golden test cases are treated as equivalent to ordinary ones. To
        test the golden function, `check` should be used instead.

        Parameters
        ----------
        under_test : Callable[ProblemParamSpec, ProblemOutputType]
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
        for score, grp in zip(scores, groups):
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

    def _virtual_groups(self) -> list[_TestInputGroup[ProblemOutputType]]:
        """Get the list of groups, plus the current group under construction.

        We need to do it this way because while the problem is being read we don't know
        the configuration of the last test group yet.
        """
        if self._ungrouped_tests or self._ungrouped_prizes:
            virtual_group: _TestInputGroup[ProblemOutputType] = _TestInputGroup()

            for case in self._ungrouped_tests:
                virtual_group.add_test_case(case)

            for prize in self._ungrouped_prizes:
                virtual_group.add_prize(prize)

            return self._groups + [virtual_group]

        else:
            return self._groups

    def __call__(self, *args, **kwargs) -> ProblemOutputType:  # type: ignore
        """Enable the ability to call the golden solution as if the problem were it."""
        return self._golden(*args, **kwargs)


def problem(
    name: Optional[str] = None,
    script: bool = False,
    check_stdout: Optional[bool] = None,
    mock_input: Optional[bool] = None,
) -> Callable[
    [Callable[ProblemParamSpec, ProblemOutputType]],
    Problem[ProblemParamSpec, ProblemOutputType],
]:
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
    Callable[[Callable[ProblemInput, T]], Problem[T]]
        A decorator which turns a golden solution into a problem.
    """
    config = AgaConfig()

    if check_stdout is not None:
        config.problem.check_stdout = check_stdout
        config.problem.check_stdout_overridden = True

    if mock_input is not None:
        config.problem.mock_input = mock_input
        config.problem.mock_input_overridden = True

    def outer(
        func: Callable[ProblemParamSpec, ProblemOutputType]
    ) -> Problem[ProblemParamSpec, ProblemOutputType]:
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


def group(
    weight: int = 1,
    value: float = 0.0,
    extra_credit: float = 0.0,
) -> Callable[
    [Problem[ProblemParamSpec, ProblemOutputType]],
    Problem[ProblemParamSpec, ProblemOutputType],
]:
    """Declare a group of problems.

    Parameters
    ----------
    weight : int
        The group's relative weight to the problem's score. See :ref:`Determining Score`
        for details.
    value : float
        The group's absolute score. See :ref:`Determining Score` for details.
    extra_credit : float
        The group's extra credit. See :ref:`Determining Score` for details.

    Returns
    -------
    Callable[[Problem[T]], Problem[T]]
        A decorator which adds the group to a problem.
    """

    def outer(
        prob: Problem[ProblemParamSpec, ProblemOutputType]
    ) -> Problem[ProblemParamSpec, ProblemOutputType]:
        prob.add_group(_TestInputGroup(weight, value, extra_credit))
        return prob

    return outer
