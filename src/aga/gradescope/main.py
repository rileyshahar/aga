"""Contains the `main` function which is used by the run_autograder script."""

from os.path import join as pathjoin
from typing import TypeVar

from ..config import AgaConfig
from ..core import Problem
from ..loader import (
    NoMatchingSymbol,
    SubmissionSyntaxError,
    TooManyMatchingSymbols,
    load_problem,
    load_symbol_from_dir,
)
from .metadata import load_submission_metadata_from_path
from .runner import GradescopeJson, run_suite

Output = TypeVar("Output")

_AUTOGRADER_ROOT = "/autograder"
_AUTOGRADER_SRC = pathjoin(_AUTOGRADER_ROOT, "source")
_AUTOGRADER_SUBMISSION = pathjoin(_AUTOGRADER_ROOT, "submission")
_AUTOGRADER_METADATA = pathjoin(_AUTOGRADER_ROOT, "submission_metadata.json")
_OUTPUT_FILE = pathjoin(_AUTOGRADER_ROOT, "results/results.json")


def gradescope_main(
    problem_src: str = _AUTOGRADER_SRC,
    submission_dir: str = _AUTOGRADER_SUBMISSION,
    metadata_file: str = _AUTOGRADER_METADATA,
    output_file: str = _OUTPUT_FILE,
) -> None:
    """Load and run the tests against student code.

    The parameters are to allow overriding the file structure in unit testing.
    """
    # if nonempty, will exit before running tests and display these to the student
    error_messages: list[str] = []

    problem = load_problem(problem_src)  # type: ignore
    metadata = load_submission_metadata_from_path(metadata_file)

    try:
        under_test = load_symbol_from_dir(
            submission_dir, problem.expected_symbol()  # pylint: disable=no-member
        )
    except SubmissionSyntaxError as err:
        error_messages.append(
            _submission_syntax_error_msg(
                err.__cause__, problem.config()  # type: ignore
            )
        )
    except NoMatchingSymbol:
        error_messages.append(_no_matches_error_msg(problem))
    except TooManyMatchingSymbols:
        error_messages.append(_too_many_matches_error_msg(problem))

    with open(output_file, "w+", encoding="UTF-8") as file:
        if error_messages:
            out = GradescopeJson()
            out.output = "\n\n".join(error_messages)
            out.score = 0.0
            # pylint: disable=no-member
            file.write(out.to_json())  # type: ignore
        else:
            # we generate the suite here because it has to be in the else, because it
            # relies on `under_test`, but we want this if/else under the open so both
            # branches can use the file stream
            suite = problem.generate_test_suite(
                under_test, metadata.assignment.total_points
            )  # pylint: disable=no-member
            run_suite(suite, file)


def _submission_syntax_error_msg(cause: SyntaxError, config: AgaConfig) -> str:
    return config.submission.import_error_msg.format(message=str(cause))


def _no_matches_error_msg(problem: Problem[Output]) -> str:
    return problem.config().submission.no_match_msg.format(
        name=problem.expected_symbol()
    )


def _too_many_matches_error_msg(problem: Problem[Output]) -> str:
    return problem.config().submission.too_many_matches_msg.format(
        name=problem.expected_symbol()
    )
