"""Contains the `main` function which is used by the run_autograder script."""

from os.path import join as pathjoin
from typing import TypeVar

from ..loader import load_problem, load_symbol_from_dir
from .metadata import load_submission_metadata_from_path
from .runner import run_suite

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
    problem = load_problem(problem_src)  # type: ignore
    under_test = load_symbol_from_dir(
        submission_dir, problem.expected_symbol()  # pylint: disable=no-member
    )
    metadata = load_submission_metadata_from_path(metadata_file)

    suite = problem.generate_test_suite(
        under_test, metadata.assignment.total_points
    )  # pylint: disable=no-member

    with open(output_file, "w+", encoding="UTF-8") as file:
        run_suite(suite, file)
