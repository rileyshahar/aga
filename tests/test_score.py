"""Tests the for score determination functionality."""

import pytest

from aga.score import ScoreInfo, compute_scores


@pytest.mark.parametrize(
    "score_infos,total_score,expected_out",
    [
        (
            [
                ScoreInfo(2, 0.0),
                ScoreInfo(0, 2.0),
                ScoreInfo(2, 4.0),
                ScoreInfo(1, 2.0),
                ScoreInfo(1, 0.0),
            ],
            20.0,
            [4, 2, 8, 4, 2],
        )
    ],
)
def test_compute_scores(
    score_infos: list[ScoreInfo], total_score: float, expected_out: list[float]
) -> None:
    """Test that compute_scores works."""
    assert compute_scores(score_infos, total_score) == expected_out
