"""Tests for the gradescope frontend."""

# this is raised whenever you access any member of the unpickled objects
# pylint: disable=no-member

import json
import os
from io import TextIOWrapper
from os.path import dirname
from os.path import join as pathjoin
from pathlib import Path
from typing import Any, Iterable, Tuple, TypeVar
from zipfile import ZipFile

import pytest
from dill import load  # type: ignore
from importlib_resources import open_text
from pytest_mock import MockerFixture

from aga.core import Problem
from aga.gradescope import InvalidProblem, into_gradescope_zip
from aga.gradescope.main import gradescope_main

Output = TypeVar("Output")


@pytest.fixture(name="gradescope_zip")
def fixture_gradescope_zip(
    valid_problem: Problem[Output],
) -> Iterable[Tuple[Problem[Output], str]]:
    """Construct a zip from a problem, returning the problem and the zip path."""

    zip_path = into_gradescope_zip(valid_problem)

    # when you yield from a pytest fixture, it runs the test immediately, and then
    # returns to the fixture for cleanup
    yield (valid_problem, zip_path)

    os.remove(zip_path)


def test_into_gradescope_zip_path(gradescope_zip: Tuple[Problem[Output], str]) -> None:
    """Test that into_gradescope_zip puts the zip file at the right plase."""

    orig_problem, zip_path = gradescope_zip

    assert zip_path == f"{orig_problem.name()}.zip"


def test_into_gradescope_zip_problem(
    gradescope_zip: Tuple[Problem[Output], str]
) -> None:
    """Test that into_gradescope_zip pickles the provided problem correctly."""

    orig_problem, zip_path = gradescope_zip

    with ZipFile(zip_path) as zip_f:
        with zip_f.open("problem.pckl") as problem:
            problem_loaded = load(problem)  # type: Problem[Output]
            problem_loaded.run_golden_tests()
            assert problem_loaded.name() == orig_problem.name()


@pytest.mark.parametrize("file", ("run_autograder", "setup.sh"))
def test_into_gradescope_zip_run_autograder(
    gradescope_zip: Tuple[Problem[Output], str], file: str
) -> None:
    """Test that into_gradescope_zip copies files correctly."""

    _, zip_path = gradescope_zip

    with ZipFile(zip_path) as zip_f:
        with zip_f.open(file, "r") as zip_byte_stream:
            with TextIOWrapper(zip_byte_stream) as zipped_file:
                with open_text("aga.gradescope.resources", file) as src:
                    assert zipped_file.read() == src.read()


def test_into_gradescope_zip_custom_path(valid_problem: Problem[Output]) -> None:
    """Test into_gradescope_zip with a custom path."""

    try:
        zip_path = into_gradescope_zip(valid_problem, "archive.zip")
        assert zip_path == "archive.zip"
    finally:
        os.remove(zip_path)


def test_into_gradescope_zip_incorrect_problem(diff_bad_impl: Problem[int]) -> None:
    """Test into_gradescope_zip with an invalid problem."""

    with pytest.raises(InvalidProblem):
        zip_path = into_gradescope_zip(diff_bad_impl)

        # should never be run if the test works, but if not, we want to clean up
        os.remove(zip_path)


@pytest.fixture(name="gs_json_square")
def fixture_gs_json_square(
    square: Problem[int], source_square: str, mocker: MockerFixture, tmp_path: Path
) -> Any:
    """Generate the JSON output from the square problem."""
    mocked_load_problem = mocker.patch("aga.gradescope.main.load_problem")
    mocked_load_problem.return_value = square

    output = pathjoin(tmp_path, "results.json")
    gradescope_main(submission_dir=dirname(source_square), output_file=output)

    with open(output, encoding="UTF-8") as file:
        return json.load(file)


def test_json_test_name_square(gs_json_square: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct test names."""
    assert set(map(lambda x: x["name"], gs_json_square["tests"])) == {
        "Test 4",
        "Test 2",
        "Test -2",
    }


def test_json_test_score_square(gs_json_square: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct score."""
    assert gs_json_square["score"] == 3


def test_json_test_visibility_square(gs_json_square: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct visibility."""
    print(gs_json_square)
    assert set(map(lambda t: t["visibility"], gs_json_square["tests"])) == {
        "visible",
        "visible",
        "hidden",
    }
