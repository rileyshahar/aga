"""Tests for the runner module."""

from aga.core import Problem
from aga.runner import AgaTestCaseOutput, load_and_run


def test_square_output(square: Problem[int], source_square: str) -> None:
    """Test the output of a typical square problem."""
    output = load_and_run(square, source_square, 20.0)

    assert (
        AgaTestCaseOutput(
            score=20 / 3,
            max_score=20 / 3,
            name="Test on 4.",
            output=None,
            hidden=False,
        )
        in output.tests
    )
    assert (
        AgaTestCaseOutput(
            score=20 / 3,
            max_score=20 / 3,
            name="Test on 2.",
            output=None,
            hidden=False,
        )
        in output.tests
    )
    assert (
        AgaTestCaseOutput(
            score=20 / 3,
            max_score=20 / 3,
            name="Test on -2.",
            output=None,
            hidden=True,
        )
        in output.tests
    )
    assert output.score == 20
    assert output.output == "Great work! Looks like you're passing all the tests."


def test_square_failure_output(
    square: Problem[int], source_square_incorrect: str
) -> None:
    """Test the output of an incorrect square problem."""
    output = load_and_run(square, source_square_incorrect, 20.0)

    assert (
        AgaTestCaseOutput(
            score=0,
            max_score=20 / 3,
            name="Test on 4.",
            output="16 != 0 : Your submission didn't give the output "
            "we expected. We checked it with 4 and got 0, but we expected 16.",
            hidden=False,
        )
        in output.tests
    )
    assert (
        AgaTestCaseOutput(
            score=0,
            max_score=20 / 3,
            name="Test on 2.",
            output="4 != 0 : Your submission didn't give the output "
            "we expected. We checked it with 2 and got 0, but we expected 4.",
            hidden=False,
        )
        in output.tests
    )
    assert (
        AgaTestCaseOutput(
            score=0,
            max_score=20 / 3,
            name="Test on -2.",
            output="4 != 0 : Your submission didn't give the output "
            "we expected. We checked it with -2 and got 0, but we expected 4.",
            hidden=True,
        )
        in output.tests
    )
    assert output.score == 0
    assert (
        output.output == "Good work, but it looks like some tests failed; take a look "
        "and see if you can fix them!\n\nSome of those tests were hidden tests, for "
        "which you won't know the inputs. In the real world, we don't always know "
        "exactly how or why our code is failing. Try to test edge cases and see if you "
        "can find the bugs!"
    )
