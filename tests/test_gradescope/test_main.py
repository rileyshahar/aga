"""Tests for the gradescope main file."""

import json
import os
from os.path import dirname
from os.path import join as pathjoin
from pathlib import Path
from typing import Any, Iterable, TypeVar

import pytest
from pytest_mock import MockerFixture

from aga.core import Problem
from aga.gradescope import into_gradescope_zip
from aga.gradescope.main import gradescope_main

Output = TypeVar("Output")

# location of resources file, for testing imports
RESOURCES_DIR = "aga.gradescope.resources"


@pytest.fixture(name="gradescope_zip")
def fixture_gradescope_zip(
    valid_problem: Problem[Output],
) -> Iterable[tuple[Problem[Output], str]]:
    """Construct a zip from a problem, returning the problem and the zip path."""

    zip_path = into_gradescope_zip(valid_problem)

    # when you yield from a pytest fixture, it runs the test immediately, and then
    # returns to the fixture for cleanup
    yield (valid_problem, zip_path)

    os.remove(zip_path)


def get_gs_json(
    problem: Problem[Any],
    source: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> Any:
    """Get the gradescope JSON output for the given problem and submission source."""
    mocked_load_problem = mocker.patch("aga.gradescope.main.load_problem")
    mocked_load_problem.return_value = problem

    output = pathjoin(tmp_path, "results.json")
    gradescope_main(
        submission_dir=dirname(source),
        metadata_file=example_metadata_file,
        output_file=output,
    )

    with open(output, encoding="UTF-8") as file:
        return json.load(file)


@pytest.fixture(name="gs_json_square")
def fixture_gs_json_square(
    square: Problem[int],
    source_square: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> Any:
    """Generate the JSON output from the square problem."""
    return get_gs_json(square, source_square, mocker, tmp_path, example_metadata_file)


def test_json_test_name_square(gs_json_square: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct test names."""
    assert set(map(lambda x: x["name"], gs_json_square["tests"])) == {
        "Test 4",
        "Test 2",
        "Test -2",
    }


def test_json_test_score_square(gs_json_square: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct score."""
    # should be 20 because that's what our metadata file says
    assert gs_json_square["score"] == 20.0


def test_json_test_visibility_square(gs_json_square: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct visibility."""
    assert set(map(lambda t: t["visibility"], gs_json_square["tests"])) == {
        "visible",
        "hidden",
    }


@pytest.fixture(name="gs_json_square_incorrect")
def fixture_gs_json_square_incorrect(
    square: Problem[int],
    source_square_incorrect: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> Any:
    """Generate the JSON output from the square problem with an incorrect submission."""
    return get_gs_json(
        square, source_square_incorrect, mocker, tmp_path, example_metadata_file
    )


def test_json_test_score_square_incorrect(gs_json_square_incorrect: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct score."""
    assert gs_json_square_incorrect["score"] == 0


def test_json_test_output_square_incorrect(gs_json_square_incorrect: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct output."""
    assert any(
        map(
            lambda t: "Checked with 2. Expected 4. Got 0 instead." in t["output"],
            gs_json_square_incorrect["tests"],
        )
    )


@pytest.fixture(name="gs_json_square_error")
def fixture_gs_json_square_error(
    square: Problem[int],
    source_square_error: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> Any:
    """Generate the JSON output from the square problem with an erroring submission."""
    return get_gs_json(
        square, source_square_error, mocker, tmp_path, example_metadata_file
    )


def test_json_test_score_square_error(gs_json_square_error: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct score."""
    assert gs_json_square_error["score"] == 0


def test_json_test_output_square_error(gs_json_square_error: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct output."""
    assert all(
        map(
            lambda t: "NameError" in t["output"],
            gs_json_square_error["tests"],
        )
    )


@pytest.fixture(name="gs_json_square_custom_name")
def fixture_gs_json_square_custom_name(
    square_custom_name: Problem[int],
    source_square: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> Any:
    """Generate the JSON output from the square problem with an erroring submission."""
    return get_gs_json(
        square_custom_name, source_square, mocker, tmp_path, example_metadata_file
    )


def test_json_test_name_square_custom_name(gs_json_square_custom_name: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct test names."""
    assert set(map(lambda x: x["name"], gs_json_square_custom_name["tests"])) == {
        "Test positive two",
        "Test minus two",
        "This is a deliberately silly name!",
    }


def test_json_test_score_square_with_weights(
    square_simple_weighted: Problem[int],
    source_square_wrong_on_zero: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    """Test that the JSON file produced by gradescope has the correct score."""
    gs_json = get_gs_json(
        square_simple_weighted,
        source_square_wrong_on_zero,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    # we have a total score of 20 and are wrong only for x=0, which has total score 8,
    # so the final score should be 12
    assert gs_json["score"] == 12