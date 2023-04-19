"""Utilities for easily computing problem score."""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .core.problem import ProblemOutputType, ProblemParamSpec
    from .core import Problem, SubmissionMetadata
    from .runner import TcOutput


PrizeCriteria = Callable[[list["TcOutput"], "SubmissionMetadata"], tuple[float, str]]


@dataclass(frozen=True)
class ScoreInfo:
    """Info to help compute a score.

    Attributes
    ----------
    value : float
        The object's absolute point value.
    weight : int
        The relative of the remaining score this object will claim.
    extra_credit : float
        The absolute extra-credit point value.
    """

    weight: int
    value: float
    extra_credit: float


def compute_scores(score_infos: list[ScoreInfo], total_score: float) -> list[float]:
    """Compute the scores of a list of scorable objects.

    Returns their scores in the same order as the initial list.
    """
    out = []
    total_weight = 0
    for s in score_infos:
        total_score -= s.value
        total_weight += s.weight

    for s in score_infos:
        if total_weight > 0:
            out.append(
                s.value + (total_score * s.weight) / total_weight + s.extra_credit
            )
        else:
            out.append(s.value + s.extra_credit)

    return out


@dataclass(frozen=True)
class Prize:
    """A points prize, which can be earned by meeting certain problem-wide criteria."""

    name: str
    criteria: PrizeCriteria
    score_info: ScoreInfo


@dataclass(frozen=True)
class ScoredPrize:
    """A prize with attached score."""

    prize: Prize
    max_score: float


def prize(
    criteria: PrizeCriteria,
    name: str = "Prize",
    weight: int = 1,
    value: float = 0.0,
    extra_credit: float = 0.0,
) -> Callable[
    [Problem[ProblemParamSpec, ProblemOutputType]],
    Problem[ProblemParamSpec, ProblemOutputType],
]:
    """Add a points prize to the problem.

    Parameters
    ----------
    criteria : Callable[[list[TcOutput], SubmissionMetadata], tuple[float, str]
        The criteria for awarding the prize's points. The first returned value should be
        a float from 0 to 1 which determines the fraction of points to assign. The
        second should be a string which will be displayed to the student.
    name : str
        The name of the prize, to be displayed to the student.
    weight : int
        The prize's weight. See :ref:`Determining Score` for details.
    value : int
        The prize's absolute score. See :ref:`Determining Score` for details.
    extra_credit : int
        The prize's extra credit. See :ref:`Determining Score` for details.

    Returns
    -------
    Callable[[Problem[T]], Problem[T]]
        A decorator which adds the prize to a problem.
    """
    to_add = Prize(name, criteria, ScoreInfo(weight, value, extra_credit))

    def inner(
        problem: Problem[ProblemParamSpec, ProblemOutputType]
    ) -> Problem[ProblemParamSpec, ProblemOutputType]:
        problem.add_prize(to_add)
        return problem

    return inner


def all_correct(tests: list["TcOutput"], _: "SubmissionMetadata") -> tuple[float, str]:
    """1.0 if all tests passed, 0.0 otherwise.

    For use as a prize.
    """
    if all(t.is_correct() for t in tests):
        return 1.0, "Good work! You earned these points since all tests passed."
    else:
        return 0.0, "To earn these points, make sure all tests pass."


def on_time(_: list["TcOutput"], metadata: "SubmissionMetadata") -> tuple[float, str]:
    """1.0 if the submission was on time, 0.0 otherwise.

    For use as a prize.
    """
    if metadata.is_on_time():
        return (
            1.0,
            "Good work! You earned these points by turning the assignment in on time.",
        )
    else:
        return (
            0.0,
            "To earn this next time, make sure to turn the assignment in on time!",
        )


def correct_and_on_time(
    tests: list["TcOutput"], metadata: "SubmissionMetadata"
) -> tuple[float, str]:
    """1.0 if the submission was correct and passed all tests, 0.0 otherwise.

    For use as a prize.
    """
    match (bool(all_correct(tests, metadata)[0]), bool(on_time(tests, metadata)[0])):
        case (True, True):
            return (
                1.0,
                "Good work! You earned these points since all tests passed and "
                "you turned in the assignment on time.",
            )
        case (False, True):
            return 0.0, "To earn these points, make sure all tests pass."
        case (True, False):
            return (
                0.0,
                "To earn these points next time, "
                "make sure to turn the assignment in on time.",
            )
        case _:
            return (
                0.0,
                "To earn these points next time, "
                "make sure to turn the assignment in on time, and that all tests pass.",
            )
