"""Tests the for score determination functionality."""

import pytest

from aga.core import SubmissionMetadata
from aga.runner import TcOutput
from aga.score import ScoreInfo, compute_scores, correct_and_on_time


@pytest.mark.parametrize(
    "score_infos,total_score,expected_out",
    [
        (
            [
                ScoreInfo(2, 0.0, 0.0),
                ScoreInfo(0, 2.0, 0.0),
                ScoreInfo(2, 4.0, 0.0),
                ScoreInfo(1, 2.0, 0.0),
                ScoreInfo(1, 0.0, 0.0),
            ],
            20.0,
            [4, 2, 8, 4, 2],
        ),
        ([ScoreInfo(1, 1.0, 0.0)], 1.0, [1.0]),
        ([ScoreInfo(0, 1.0, 0.0)], 1.0, [1.0]),
        ([ScoreInfo(2, 0.0, 1.0), ScoreInfo(1, 0.0, 0.0)], 18.0, [13.0, 6.0]),
    ],
)
def test_compute_scores(
    score_infos: list[ScoreInfo], total_score: float, expected_out: list[float]
) -> None:
    """Test that compute_scores works."""
    assert compute_scores(score_infos, total_score) == expected_out


def test_correct_and_on_time(metadata: SubmissionMetadata) -> None:
    """Test that correct_and_on_time works."""
    assert correct_and_on_time([], metadata) == (
        1.0,
        "Good work! You earned these points since all tests passed and "
        "you turned in the assignment on time.",
    )


def test_correct_and_on_time_false(metadata: SubmissionMetadata) -> None:
    """Test that correct_and_on_time works when wrong."""
    assert correct_and_on_time(
        [TcOutput(score=0.0, max_score=1.0, name="Example", status="failed")], metadata
    ) == (0.0, "To earn these points, make sure all tests pass.")


def test_correct_and_on_time_both_false(metadata_late: SubmissionMetadata) -> None:
    """Test that correct_and_on_time works when wrong and late."""
    # pylint: disable=unsubscriptable-object
    assert correct_and_on_time(
        [TcOutput(score=0.0, max_score=1.0, name="Example", status="failed")],
        metadata_late,
    ) == (
        0.0,
        "To earn these points next time, "
        "make sure to turn the assignment in on time, and that all tests pass.",
    )
