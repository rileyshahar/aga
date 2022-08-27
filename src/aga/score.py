"""Compute a problem's score."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .core import SubmissionMetadata
    from .runner import AgaProblemOutput

ScoreExtra = Callable[["AgaProblemOutput", "SubmissionMetadata"], bool]


def prize(output: "AgaProblemOutput", metadata: "SubmissionMetadata") -> bool:
    """Return true if all tests passed and the submission was on time."""
    return metadata.is_on_time() and all(t.is_correct() for t in output.tests)


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
