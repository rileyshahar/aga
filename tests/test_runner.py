"""Tests for the runner module."""

from os.path import dirname

from aga.core import Output, Problem
from aga.loader import load_symbol_from_dir
from aga.runner import AgaProblemOutput, AgaTestCaseOutput, run


def get_problem_out(
    problem: Problem[Output],
    submission_source: str,
) -> AgaProblemOutput:
    """Get the problem output for the given problem and submission at `source`."""
    under_test = load_symbol_from_dir(
        dirname(submission_source), problem.expected_symbol()
    )
    suite = problem.generate_test_suite(under_test, 20.0)
    return run(suite)


def test_square_output(square: Problem[int], source_square: str) -> None:
    """Test the output of a typical square problem."""
    output = get_problem_out(square, source_square)

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
    output = get_problem_out(square, source_square_incorrect)

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
