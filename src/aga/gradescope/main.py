"""Contains the `main` function which is used by the run_autograder script."""

from os.path import join as pathjoin
from typing import TypeVar

from ..loader import load_problem
from ..runner import load_and_run
from .metadata import load_submission_metadata_from_path
from .schema import write_to

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
    metadata = load_submission_metadata_from_path(
        metadata_file
    ).to_submission_metadata()
    output = load_and_run(problem, submission_dir, metadata)

    with open(output_file, "w+", encoding="UTF-8") as file:
        write_to(output, file)
