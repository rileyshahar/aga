"""Contains fixtures for gradescope-specific testing."""
from importlib.resources import files
from os.path import join as pathjoin
from pathlib import Path
from shutil import copyfileobj

import pytest

from aga.gradescope.metadata import (
    GradescopeSubmissionMetadata,
    load_submission_metadata_from_path,
)


@pytest.fixture(name="example_metadata_file")
def fixture_example_metadata_file(tmp_path: Path) -> str:
    """Get a path with the example metadata file from the gradescope documentation."""
    path = pathjoin(tmp_path, "metadata.json")

    with files("tests.test_gradescope.resources").joinpath(  # type: ignore
        "example_metadata.json"
    ).open() as src:
        with open(pathjoin(tmp_path, "metadata.json"), "w", encoding="UTF-8") as dest:
            copyfileobj(src, dest)

    return path


@pytest.fixture(name="example_metadata")
def fixture_example_metadata(
    example_metadata_file: str,
) -> GradescopeSubmissionMetadata:
    """Get the example metadata file from the gradescope documentation."""
    return load_submission_metadata_from_path(example_metadata_file)
