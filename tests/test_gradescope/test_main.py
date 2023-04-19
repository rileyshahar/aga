"""Tests for the gradescope main file."""

import json
from os.path import dirname
from os.path import join as pathjoin
from pathlib import Path
from typing import Any, TypeVar

import pytest
from pytest_mock import MockerFixture

from aga import problem as agaproblem
from aga.core import Problem
from aga.gradescope.main import gradescope_main
from aga.runner import TcOutput

Output = TypeVar("Output")


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
    assert set(map(lambda x: x["name"], gs_json_square["tests"])) == {  # type: ignore
        "Test on 4.",
        "Test on 2.",
        "Test on -2.",
    }


def test_json_test_score_square(gs_json_square: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct score."""
    # should be 20 because that's what our metadata file says
    assert gs_json_square["score"] == 20.0


def test_json_test_visibility_square(gs_json_square: Any) -> None:
    """Test that the JSON file produced by gradescope has the correct visibility."""
    assert set(
        map(lambda t: t["visibility"], gs_json_square["tests"])  # type: ignore
    ) == {
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
    print(gs_json_square_incorrect["tests"])
    assert any(
        map(
            lambda t: t["output"]
            == TcOutput.format_rich_output(
                error_description=(
                    "Your submission didn't give the output "
                    "we expected. We checked it with 2 and got 0, but we expected 4."
                )
            ),
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
            lambda t: "A python NameError occured while running your submission: "
            "name 'y' is not defined." in t["output"],
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
    assert set(
        map(lambda x: x["name"], gs_json_square_custom_name["tests"])  # type: ignore
    ) == {
        "Test positive two.",
        "Test minus two.",
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


def test_json_test_score_square_grouped(
    square_grouped: Problem[int],
    source_square_wrong_on_zero: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    """Test that the JSON file produced by gradescope has the correct score."""
    gs_json = get_gs_json(
        square_grouped,
        source_square_wrong_on_zero,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    # we have a total score of 20 and are wrong only for x=0, which has total score 12,
    # so the final score should be 8
    assert gs_json["score"] == 8


def test_json_square_generated_cases(
    square_generated_cases: Problem[int],
    source_square_wrong_on_zero: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    """Test that the JSON file includes the right test cases."""
    gs_json = get_gs_json(
        square_generated_cases,
        source_square_wrong_on_zero,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    # there should
    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -2.",
        "Test on -1.",
        "Test on 0.",
        "Test on 1.",
        "Test on 2.",
    }


def test_json_diff_generated_cases(
    diff_generated: Problem[int],
    source_diff: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    """Test that the JSON file includes the right test cases."""
    gs_json = get_gs_json(
        diff_generated,
        source_diff,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    # there should
    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -1,-1.",
        "Test on 0,-1.",
        "Test on 1,-1.",
        "Test on -1,0.",
        "Test on 0,0.",
        "Test on 1,0.",
        "Test on -1,1.",
        "Test on 0,1.",
        "Test on 1,1.",
    }


def test_json_pos_zip(
    pos_zip: Problem[int],
    source_diff: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    gs_json = get_gs_json(
        pos_zip,
        source_diff,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -1,1.",
        "Test on 1,3.",
    }


def test_json_pos_zip_with_singleton_aga_args(
    pos_zip_with_singleton_aga_args: Problem[int],
    source_diff: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    gs_json = get_gs_json(
        pos_zip_with_singleton_aga_args,
        source_diff,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -1,1.",
        "Test on 1,3.",
    }


def test_json_aga_args_in_product(
    aga_args_in_product: Problem[int],
    source_diff: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    gs_json = get_gs_json(
        aga_args_in_product,
        source_diff,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -1,1.",
        "Test on -1,2.",
        "Test on 0,1.",
        "Test on 0,2.",
        "Test on 1,1.",
        "Test on 1,2.",
    }


def test_json_aga_args_with_kwargs_in_product(
    aga_args_with_kwargs_in_product: Problem[int],
    source_diff: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    gs_json = get_gs_json(
        aga_args_with_kwargs_in_product,
        source_diff,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -1,y=1.",
        "Test on -1,y=2.",
        "Test on 0,y=1.",
        "Test on 0,y=2.",
        "Test on 1,y=1.",
        "Test on 1,y=2.",
    }


def test_json_aga_args_with_kwargs_in_product_singleton(
    aga_args_with_kwargs_in_product_singleton: Problem[int],
    source_diff: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    gs_json = get_gs_json(
        aga_args_with_kwargs_in_product_singleton,
        source_diff,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -1,y=1.",
        "Test on -1,y=2.",
        "Test on 0,y=1.",
        "Test on 0,y=2.",
        "Test on 1,y=1.",
        "Test on 1,y=2.",
    }


def test_json_aga_args_singleton(
    aga_args_singleton: Problem[int],
    source_diff: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    gs_json = get_gs_json(
        aga_args_singleton,
        source_diff,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -1,1.",
        "Test on -1,2.",
        "Test on 0,1.",
        "Test on 0,2.",
        "Test on 1,1.",
        "Test on 1,2.",
    }


def test_json_diff_kwarg_generated_cases_no_product(
    pos_and_kwd_zip: Problem[int],
    source_diff: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    """Test that the JSON file includes the right test cases."""
    gs_json = get_gs_json(
        pos_and_kwd_zip,
        source_diff,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    # there should
    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -1,y=-1.",
        "Test on 0,y=0.",
        "Test on 1,y=1.",
    }


def test_json_diff_kwarg_generated_cases(
    pos_and_kwd_generated: Problem[int],
    source_diff: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    """Test that the JSON file includes the right test cases."""
    gs_json = get_gs_json(
        pos_and_kwd_generated,
        source_diff,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    # there should
    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -1,y=-1.",
        "Test on 0,y=-1.",
        "Test on 1,y=-1.",
        "Test on -1,y=0.",
        "Test on 0,y=0.",
        "Test on 1,y=0.",
        "Test on -1,y=1.",
        "Test on 0,y=1.",
        "Test on 1,y=1.",
    }


def test_json_diff_kwarg_custom_generator(
    pos_and_kwd_generator_function: Problem[int],
    source_diff: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    """Test that the JSON file includes the right test cases."""
    gs_json = get_gs_json(
        pos_and_kwd_generator_function,
        source_diff,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    # there should
    assert set(map(lambda t: t["name"], gs_json["tests"])) == {  # type: ignore
        "Test on -1,y=-1.",
        "Test on 0,y=-1.",
        "Test on 1,y=-1.",
        "Test on -1,y=0.",
        "Test on 0,y=0.",
        "Test on 1,y=0.",
        "Test on -1,y=1.",
        "Test on 0,y=1.",
        "Test on 1,y=1.",
    }


def test_json_invalid_source(
    square: Problem[int],
    source_invalid: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    """Test that the error message is correct."""
    gs_json = get_gs_json(
        square,
        source_invalid,
        mocker,
        tmp_path,
        example_metadata_file,
    )

    assert gs_json["score"] == 0.0
    assert "invalid syntax" in gs_json["output"]
    assert (
        "Looks like there's a python error in your code that prevented "
        "us from running tests: " in gs_json["output"]
    )
    assert (
        "Please fix this error, test your code again, and then resubmit."
        in gs_json["output"]
    )


def test_json_no_matching_symbol(
    diff: Problem[int],
    source_dir: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    """Test that the error message is correct."""
    # source_dir has no solution for diff, so this should error
    gs_json = get_gs_json(
        diff,
        # we join square.py because get_gs_json calls dirname
        pathjoin(source_dir, "square.py"),
        mocker,
        tmp_path,
        example_metadata_file,
    )

    assert gs_json["score"] == 0.0
    assert gs_json["output"] == (
        "It looks like you didn't include the right object; we were looking for "
        "something named `difference`. Please resumbit with the correct name."
    )


def test_json_too_many_matching_symbols(
    source_dir: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> None:
    """Test that the error message is correct."""

    # source_dir has no solution for diff, so this should error
    @agaproblem()
    def duplicate() -> None:
        """Mock problem because we want to expect this name."""

    gs_json = get_gs_json(
        duplicate,
        # we join square.py because get_gs_json calls dirname
        pathjoin(source_dir, "square.py"),
        mocker,
        tmp_path,
        example_metadata_file,
    )

    assert gs_json["score"] == 0.0
    assert gs_json["output"] == (
        "It looks like multiple files you submitted have objects named `duplicate`; "
        "unfortunately, we can't figure out which one is supposed to be the real "
        "submission. Please remove all but one of them and resumbit."
    )


@pytest.fixture(name="gs_json_bad_override_description")
def fixture_gs_json_override_description(
    override_description: Problem[int],
    source_bad_override_description: str,
    mocker: MockerFixture,
    tmp_path: Path,
    example_metadata_file: str,
) -> Any:
    return get_gs_json(
        override_description,
        source_bad_override_description,
        mocker,
        tmp_path,
        example_metadata_file,
    )


@pytest.mark.parametrize(
    "target",
    [
        TcOutput.format_rich_output(
            description="This is a custom description.",
            error_description="True != False",
        ),
        TcOutput.format_rich_output(
            description="This is a pre-defined description.",
        ),
        TcOutput.format_rich_output(
            description="This is a custom description.",
        ),
    ],
)
def test_json_override_description(
    gs_json_bad_override_description: Any, target: str
) -> None:
    """Test that the JSON file includes the right test cases."""
    assert any(
        map(
            lambda t: t["output"] == target,
            gs_json_bad_override_description["tests"],
        )
    )


@pytest.mark.parametrize(
    "target", ["30 is a special number", "Test on 20.", "Test on 10."]
)
def test_json_override_name(gs_json_bad_override_description: Any, target: str) -> None:
    assert any(
        map(
            lambda t: t["name"] == target,
            gs_json_bad_override_description["tests"],
        )
    )
