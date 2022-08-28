"""Compute a problem's score."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from .core import Output, Problem, SubmissionMetadata
    from .runner import TcOutput


PrizeCriteria = Callable[[list["TcOutput"], "SubmissionMetadata"], bool]


@dataclass(frozen=True)
class ScoreInfo:
    """Info to help compute a score.

    Attributes
    ----------
    value : float
        The object's absolute point value.
    weight : int
        The relative of the remaining score this object will claim.
    """

    weight: int
    value: float


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
        out.append(s.value + (total_score * s.weight) / total_weight)

    return out


@dataclass(frozen=True)
class Prize:
    """A points prize, which can be earned by meeting certain problem-wide criteria."""

    name: str
    message: Optional[str]
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
    message: Optional[str] = None,
) -> Callable[["Problem[Output]"], "Problem[Output]"]:
    """Add a points prize to the problem."""
    # TODO: docs
    to_add = Prize(name, message, criteria, ScoreInfo(weight, value))

    def inner(problem: "Problem[Output]") -> "Problem[Output]":
        problem.add_prize(to_add)
        return problem

    return inner


def all_correct(tests: list["TcOutput"], _: "SubmissionMetadata") -> bool:
    """Check whether all tests passed."""
    return all(t.is_correct() for t in tests)


def on_time(_: list["TcOutput"], metadata: "SubmissionMetadata") -> bool:
    """Check whether the submission was on-time."""
    return metadata.is_on_time()


def correct_and_on_time(
    tests: list["TcOutput"], metadata: "SubmissionMetadata"
) -> bool:
    """Check whether the submission was correct and passed all tests."""
    return all_correct(tests, metadata) and on_time(tests, metadata)
