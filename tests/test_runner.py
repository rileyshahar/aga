"""Tests for the runner module."""

from aga.core import Problem, SubmissionMetadata
from aga.runner import TcOutput, load_and_run


def test_square_output(
    square: Problem[int],
    source_square: str,
    metadata: SubmissionMetadata,
) -> None:
    """Test the output of a typical square problem."""
    output = load_and_run(square, source_square, metadata)

    assert (
        TcOutput(
            score=20 / 3,
            max_score=20 / 3,
            name="Test on 4.",
            output=None,
            hidden=False,
        )
        in output.tests
    )
    assert (
        TcOutput(
            score=20 / 3,
            max_score=20 / 3,
            name="Test on 2.",
            output=None,
            hidden=False,
        )
        in output.tests
    )
    assert (
        TcOutput(
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
    square: Problem[int], source_square_incorrect: str, metadata: SubmissionMetadata
) -> None:
    """Test the output of an incorrect square problem."""
    output = load_and_run(square, source_square_incorrect, metadata)

    assert (
        TcOutput(
            score=0,
            max_score=20 / 3,
            name="Test on 4.",
            output="Your submission didn't give the output we expected. "
            "We checked it with 4 and got 0, but we expected 16.",
            hidden=False,
        )
        in output.tests
    )
    assert (
        TcOutput(
            score=0,
            max_score=20 / 3,
            name="Test on 2.",
            output="Your submission didn't give the output we expected. "
            "We checked it with 2 and got 0, but we expected 4.",
            hidden=False,
        )
        in output.tests
    )
    assert (
        TcOutput(
            score=0,
            max_score=20 / 3,
            name="Test on -2.",
            output="Your submission didn't give the output we expected. "
            "We checked it with -2 and got 0, but we expected 4.",
            hidden=True,
        )
        in output.tests
    )
    assert output.score == 0
    assert (
        output.output == "It looks like some tests failed; take a look "
        "and see if you can fix them!\n\nSome of those tests were hidden tests, for "
        "which you won't know the inputs. In the real world, we don't always know "
        "exactly how or why our code is failing. Try to test edge cases and see if you "
        "can find the bugs!"
    )


def test_hello_world(
    hello_world: Problem[None], source_hello_world: str, metadata: SubmissionMetadata
) -> None:
    """Test the output of an incorrect hello world submission."""
    output = load_and_run(hello_world, source_hello_world, metadata)

    assert output.tests == [
        TcOutput(
            score=20.0,
            max_score=20.0,
            name="Test on .",
            output=None,
            hidden=False,
        )
    ]
    assert output.score == 20.0
    assert output.output == "Great work! Looks like you're passing all the tests."


# flake8: noqa
# pylint:disable=line-too-long
HELLO_WORLD_FAILURE_OUT = """Your submission printed something different from what we expected. We checked it with .

Here's a detailed look at the difference between the strings. Lines starting with `-` are what we got from you, lines starting with `+` are what we expected, and `_`s in lines starting with `?` denote characters that are different. Be wary for spaces, which don't show up well in this format.

- hello, world.
? ^           ^
+ Hello, world!
? ^           ^
"""


def test_hello_world_failure(
    hello_world: Problem[None],
    source_hello_world_incorrect: str,
    metadata: SubmissionMetadata,
) -> None:
    """Test the output of an incorrect hello world submission."""
    output = load_and_run(hello_world, source_hello_world_incorrect, metadata)

    assert output.tests == [
        TcOutput(
            score=0.0,
            max_score=20.0,
            name="Test on .",
            output=HELLO_WORLD_FAILURE_OUT,
            hidden=False,
        )
    ]
    assert output.score == 0
    assert output.output == (
        "It looks like some tests failed; take a look and see if you can fix them!"
    )


def test_hello_world_script(
    hello_world_script: Problem[None],
    source_hello_world_script: str,
    metadata: SubmissionMetadata,
) -> None:
    """Test the output of a correct hello world script submission."""
    output = load_and_run(hello_world_script, source_hello_world_script, metadata)

    assert output.tests == [
        TcOutput(
            score=20.0,
            max_score=20.0,
            name="Test on .",
            output=None,
            hidden=False,
        )
    ]
    assert output.score == 20.0
    assert output.output == "Great work! Looks like you're passing all the tests."


def test_hello_name(
    hello_name: Problem[None], source_hello_name: str, metadata: SubmissionMetadata
) -> None:
    """Test the output of a correct hello name submission."""
    output = load_and_run(hello_name, source_hello_name, metadata)

    assert (
        TcOutput(
            score=10.0,
            max_score=10.0,
            name="Test on 'world','me'.",
            output=None,
            hidden=False,
        )
        in output.tests
    )
    assert (
        TcOutput(
            score=10.0,
            max_score=10.0,
            name="Test on 'Alice','Bob'.",
            output=None,
            hidden=False,
        )
        in output.tests
    )

    assert output.score == 20.0
    assert output.output == "Great work! Looks like you're passing all the tests."


# flake8: noqa
# pylint:disable=line-too-long
HELLO_NAME_FAILURE_OUT_ME = """Your submission printed something different from what we expected. We checked it with 'world','me'.

Here's a detailed look at the difference between the strings. Lines starting with `-` are what we got from you, lines starting with `+` are what we expected, and `_`s in lines starting with `?` denote characters that are different. Be wary for spaces, which don't show up well in this format.

- Hello, me.
- I'm world.
+ Hello, world.
+ I'm me.
"""

# flake8: noqa
# pylint:disable=line-too-long
HELLO_NAME_FAILURE_OUT_ALICE = """Your submission printed something different from what we expected. We checked it with 'Alice','Bob'.

Here's a detailed look at the difference between the strings. Lines starting with `-` are what we got from you, lines starting with `+` are what we expected, and `_`s in lines starting with `?` denote characters that are different. Be wary for spaces, which don't show up well in this format.

- Hello, Bob.
- I'm Alice.
+ Hello, Alice.
+ I'm Bob.
"""


def test_hello_name_incorrect(
    hello_name: Problem[None],
    source_hello_name_incorrect: str,
    metadata: SubmissionMetadata,
) -> None:
    """Test the output of an incorrect hello name submission."""
    output = load_and_run(hello_name, source_hello_name_incorrect, metadata)

    assert (
        TcOutput(
            score=0.0,
            max_score=10.0,
            name="Test on 'world','me'.",
            output=HELLO_NAME_FAILURE_OUT_ME,
            hidden=False,
        )
        in output.tests
    )
    assert (
        TcOutput(
            score=0.0,
            max_score=10.0,
            name="Test on 'Alice','Bob'.",
            output=HELLO_NAME_FAILURE_OUT_ALICE,
            hidden=False,
        )
        == output.tests[1]
    )

    assert output.score == 0.0
    assert output.output == (
        "It looks like some tests failed; take a look and see if you can fix them!"
    )


def test_multiple_scripts(
    hello_world_script: Problem[None], source_dir: str, metadata: SubmissionMetadata
) -> None:
    """Test the error message when multiple scripts are uploaded."""
    output = load_and_run(hello_world_script, source_dir, metadata)

    assert output.score == 0.0
    assert (
        output.output
        == "It looks like you uploaded multiple python scripts. Please make sure you only upload one file ending in `.py`."
    )
    assert output.tests == []


def test_no_scripts(
    hello_world_script: Problem[None], tmpdir: str, metadata: SubmissionMetadata
) -> None:
    """Test the error message when no scripts are uploaded."""
    output = load_and_run(hello_world_script, tmpdir, metadata)

    assert output.score == 0.0
    assert (
        output.output
        == "It looks like you didn't upload a python script. Please make sure your script ends in `.py`."
    )
    assert output.tests == []


def test_square_prize(
    square_prize: Problem[int],
    source_square: str,
    metadata: SubmissionMetadata,
) -> None:
    """Test the output of a correct submission to the prize square problem."""
    output = load_and_run(square_prize, source_square, metadata)

    assert (
        TcOutput(
            score=20.0 / 3,
            max_score=20.0 / 3,
            name="Test on 0.",
            output=None,
            hidden=False,
        )
        in output.tests
    )
    assert (
        TcOutput(
            score=20.0 / 3,
            max_score=20.0 / 3,
            name="Test on 2.",
            output=None,
            hidden=False,
        )
        in output.tests
    )
    assert (
        TcOutput(
            score=20.0 / 3,
            max_score=20.0 / 3,
            name="Prize: correct and on time",
            output=(
                "Good work! You earned these points since all tests passed and "
                "you turned in the assignment on time."
            ),
            hidden=False,
        )
        == output.tests[2]
    )

    assert output.score == 20.0
    assert output.output == "Great work! Looks like you're passing all the tests."


def test_square_prize_late(
    square_prize: Problem[int],
    source_square: str,
    metadata_late: SubmissionMetadata,
) -> None:
    """Test the output of a late submission."""
    output = load_and_run(square_prize, source_square, metadata_late)

    assert (
        TcOutput(
            score=20.0 / 3,
            max_score=20.0 / 3,
            name="Test on 0.",
            output=None,
            hidden=False,
        )
        in output.tests
    )
    assert (
        TcOutput(
            score=20.0 / 3,
            max_score=20.0 / 3,
            name="Test on 2.",
            output=None,
            hidden=False,
        )
        in output.tests
    )
    assert (
        TcOutput(
            score=0.0 / 3,
            max_score=20.0 / 3,
            name="Prize: correct and on time",
            output=(
                "To earn these points next time, "
                "make sure to turn the assignment in on time."
            ),
            hidden=False,
        )
        in output.tests
    )

    assert output.score == 20.0 / 3 * 2
    assert output.output == "Great work! Looks like you're passing all the tests."


def test_square_prize_grouped_score(
    square_prize_grouped: Problem[int],
    source_square: str,
    metadata_late: SubmissionMetadata,
) -> None:
    """Test that square_prize_grouped assigned points correctly."""
    output = load_and_run(square_prize_grouped, source_square, metadata_late)
    # both tests pass, that's 2/5 of the 20 points
    assert output.score == 8.0


def test_square_custom_prize_score(
    square_custom_prize: Problem[int],
    source_square: str,
    metadata_previous_submissions: SubmissionMetadata,
) -> None:
    """Test that square_prize_grouped assigned points correctly."""
    output = load_and_run(
        square_custom_prize, source_square, metadata_previous_submissions
    )
    # test passes, which is 10 points; prize should be 8/10
    assert output.score == 18.0
