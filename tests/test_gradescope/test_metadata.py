"""Tests for the submission metadata parser."""

from importlib.resources import files
from os.path import join as pathjoin
from pathlib import Path
from shutil import copyfileobj

import pytest

from aga.gradescope.metadata import (
    GradescopeAssignmentMetadata,
    GradescopeSubmissionMetadata,
    load_submission_metadata_from_path,
)


def test_example_metadata_id(example_metadata: GradescopeSubmissionMetadata) -> None:
    """Test that the example metadata file's id is correct."""
    assert example_metadata.id == 123456


def test_example_metadata_upload(
    example_metadata: GradescopeSubmissionMetadata,
) -> None:
    """Test that the example metadata file's upload is correct."""
    assert example_metadata.submission_method == "upload"


def test_example_metadata_created_at(
    example_metadata: GradescopeSubmissionMetadata,
) -> None:
    """Test that the example metadata file's created at is correct."""
    time = example_metadata.created_at
    assert time.year == 2018
    assert time.month == 7
    assert time.day == 1
    assert time.hour == 14
    assert time.minute == 22
    assert time.second == 32


def test_example_metadata_previous_submissions(
    example_metadata: GradescopeSubmissionMetadata,
) -> None:
    """Test that the example metadata file's previous submissions is empty."""
    assert example_metadata.previous_submissions == []


def test_example_metadata_users(
    example_metadata: GradescopeSubmissionMetadata,
) -> None:
    """Test that the example metadata file's previous user is correct."""
    users = example_metadata.users
    assert len(users) == 1

    user = users[0]
    assert user.email == "student@example.com"
    assert user.id == 1234
    assert user.name == "Student User"


@pytest.fixture(name="example_metadata_assignment")
def fixture_example_metadata_assignment(
    example_metadata: GradescopeSubmissionMetadata,
) -> GradescopeAssignmentMetadata:
    """Get the example metadata's assignment object."""
    return example_metadata.assignment


def test_example_assignment_metadata_name(
    example_metadata_assignment: GradescopeAssignmentMetadata,
) -> None:
    """Test that the example metadata's assignment's name is correct."""
    assert example_metadata_assignment.title == "Programming Assignment 1"


@pytest.fixture(name="late_due_date_metadata")
def fixture_late_due_date_metadata(tmp_path: Path) -> GradescopeSubmissionMetadata:
    """Get a path with the example metadata file from the gradescope documentation."""
    path = pathjoin(tmp_path, "metadata.json")

    with files("tests.test_gradescope.resources").joinpath(  # type: ignore
        "metadata_with_late_due_date.json"
    ).open() as src:
        with open(path, "w", encoding="UTF-8") as dest:
            copyfileobj(src, dest)

    return load_submission_metadata_from_path(path)


def test_late_due_date(late_due_date_metadata: GradescopeSubmissionMetadata) -> None:
    """Test that we properly loda late due dates."""
    assert late_due_date_metadata.assignment.late_due_date is not None
    assert late_due_date_metadata.assignment.late_due_date.year == 2022
    assert late_due_date_metadata.assignment.late_due_date.month == 8
