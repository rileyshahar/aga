"""Compute a problem's score."""

from dataclasses import dataclass


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
