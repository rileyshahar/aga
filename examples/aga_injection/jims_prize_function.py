from aga.core import SubmissionMetadata
from aga.runner import TcOutput


def prize_fn(tests: list[TcOutput], metadata: SubmissionMetadata) -> tuple[float, str]:
    """Determine the score for our custom prize points.

    The semantics are as follows:
        * if the submission is late, award no prize
        * if there are failing tests, award no prize
        * otherwise,
            * if there were 0-2 submissions, award the full prize
            * if there were 3-6 submissions, award 80% of the prize
            * if there were 7+ submissions, award 50% of the prize
    """
    match (metadata.is_on_time(), all(t.is_correct() for t in tests)):
        case (True, True):
            pass

        case (True, False):
            return (0.0, "To earn these points, make sure all tests pass!")

        case (False, True):
            return (
                0.0,
                "Great work making all tests pass. Unfortunately, we can't offer you "
                "prize points, because this was submitted after the deadline.",
            )

        case (False, False):
            return (0.0, None)

    # here we use strict inequality because previous submissions doesn't count the
    # current one.
    if metadata.previous_submissions < 2:
        return (
            1.0,
            "Great work passing the tests! You submitted "
            f"{metadata.previous_submissions} times, "
            "and so you earned the full prize points.",
        )
    elif metadata.previous_submissions < 6:
        return (
            0.8,
            "Great work passing the tests! You submitted "
            f"{metadata.previous_submissions} times, "
            "and so you earned 80% of the prize points.",
        )
    else:
        return (
            0.5,
            "Great work passing the tests! You submitted "
            f"{metadata.previous_submissions} times, "
            "and so you earned 50% of the prize points. "
            "We recommend trying as much as possible to test on your local machine.",
        )
