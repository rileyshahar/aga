"""Tests for the command-line interfact."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from aga.cli import aga_app
from aga.cli.app import FRONTENDS, complete_frontend
from aga.core import Problem

AnyProblem = Problem[Any, Any]

runner = CliRunner(mix_stderr=False)


# pylint: disable=unused-argument
@pytest.fixture(name="mocked_lpfp")
def fixture_mocked_lpfp(mocker: MockerFixture, injection_tear_down: None) -> MagicMock:
    """Generate a mocked `load_problems_from_path`."""
    return mocker.patch("aga.cli.app.load_problems_from_path")


# pylint: disable=unused-argument
@pytest.fixture(name="mocked_igz")
def fixture_mocked_igz(mocker: MockerFixture, injection_tear_down: None) -> MagicMock:
    """Generate a mocked `into_gradescope_zip`."""
    return mocker.patch("aga.cli.app.into_gradescope_zip")


def test_gen_gradescope(
    mocked_lpfp: MagicMock, mocked_igz: MagicMock, square: Problem[[int], int]
) -> None:
    """Test that gen_gradescope works correctly."""
    mocked_lpfp.return_value = [square]
    mocked_igz.return_value = "square.zip"

    result = runner.invoke(aga_app, ["gen", "square.py"])

    mocked_lpfp.assert_called_once()
    mocked_igz.assert_called_once()

    assert "square.zip" in result.stdout
    assert result.exit_code == 0


def test_gen_gradescope_no_match(mocked_lpfp: MagicMock, mocked_igz: MagicMock) -> None:
    """Test that gen_gradescope errors with no matching symbol."""
    mocked_lpfp.return_value = []
    result = runner.invoke(aga_app, ["gen", "square.py"])

    mocked_lpfp.assert_called_once()
    mocked_igz.assert_not_called()

    assert result.stderr == "No problems found at square.py.\n"
    assert result.exit_code == 1


def test_gen_gradescope_multiple_matches(
    mocked_lpfp: MagicMock,
    mocked_igz: MagicMock,
    square: Problem[[int], int],
    diff: Problem[[int, int], int],
) -> None:
    """Test that gen_gradescope errors with multiple matching symbols."""
    mocked_lpfp.return_value = [square, diff]
    result = runner.invoke(aga_app, ["gen", "square.py"])

    mocked_lpfp.assert_called_once()
    mocked_igz.assert_not_called()

    assert result.stderr == (
        "Multiple problems found in square.py. "
        "Currently, only one problem is supported per file.\n"
    )
    assert result.exit_code == 1


def test_gen_invalid_frontend(
    mocked_lpfp: MagicMock, mocked_igz: MagicMock, valid_problem: AnyProblem
) -> None:
    """Test that gen_gradescope errors with an invalid frontend."""
    mocked_lpfp.return_value = [valid_problem]

    result = runner.invoke(aga_app, ["gen", "square", "--frontend", "doesnt-exist"])

    mocked_lpfp.assert_called_once()
    mocked_igz.assert_not_called()

    assert "invalid frontend" in result.stderr
    assert result.exit_code == 1


def test_run(
    mocked_lpfp: MagicMock,
    square: Problem[[int], int],
    source_square: str,
) -> None:
    """Test that gen_gradescope works correctly."""
    mocked_lpfp.return_value = [square]

    result = runner.invoke(aga_app, ["run", "square.py", source_square])

    mocked_lpfp.assert_called_once()

    # not going to test the whole CLI ui right now
    assert "20.0" in result.stdout
    assert result.exit_code == 0


def test_run_failing(
    mocked_lpfp: MagicMock,
    square: Problem[[int], int],
    source_square_incorrect: str,
) -> None:
    """Test that gen_gradescope works correctly."""
    mocked_lpfp.return_value = [square]

    result = runner.invoke(aga_app, ["run", "square.py", source_square_incorrect])

    mocked_lpfp.assert_called_once()

    # not going to test the whole CLI ui right now
    assert "0.0" in result.stdout
    assert result.exit_code == 0


def test_check_valid_problem(mocked_lpfp: MagicMock, valid_problem: AnyProblem) -> None:
    """Test that check succeeds with a valid problem."""
    mocked_lpfp.return_value = [valid_problem]

    result = runner.invoke(aga_app, ["check", valid_problem.name()])

    mocked_lpfp.assert_called_once()

    assert "passed golden tests" in result.stdout
    assert result.exit_code == 0


def test_check_invalid_problem(
    mocked_lpfp: MagicMock, diff_bad_gt: Problem[[int], int]
) -> None:
    """Test that check fails with an invalid problem."""
    mocked_lpfp.return_value = [diff_bad_gt]

    result = runner.invoke(aga_app, ["check", diff_bad_gt.name()])

    mocked_lpfp.assert_called_once()

    print(result.stdout)
    print(result.stderr)

    assert "failed some golden tests" in result.stderr
    assert result.exit_code == 1


def test_check_with_override(
    mocked_lpfp: MagicMock, overridden_problem: AnyProblem
) -> None:
    """Test that check succeeds with a valid problem."""
    overridden_problem.check()


def test_invalid_check_with_override(
    mocked_lpfp: MagicMock, invalid_overridden_problem: AnyProblem
) -> None:
    """Test that check fails with an invalid problem."""
    with pytest.raises(
        AssertionError, match="Your solution doesn't pass the overridden test|check."
    ):
        invalid_overridden_problem.check()


def test_complete_frontend_empty() -> None:
    """Check that complete_frontend works with an empty string."""
    assert tuple(complete_frontend("")) == FRONTENDS


def test_complete_frontend_incomplete() -> None:
    """Check that complete_frontend works with an incomplete string."""
    assert tuple(complete_frontend("grade")) == FRONTENDS


def test_complete_frontend_no_match() -> None:
    """Check that complete_frontend works with a non-matching string."""
    assert not tuple(complete_frontend("nonexistent"))


@pytest.fixture()
def mocked_injecting_func(mocker: MockerFixture) -> MagicMock:
    """Generate a mocked injecting function."""
    return mocker.patch("aga.cli.app._load_injection_config")


# pylint: disable=unused-argument, redefined-outer-name
def test_injection_is_called(mocked_injecting_func: MagicMock) -> None:
    """Check that the injection function is called."""
    runner.invoke(aga_app, ["gen", "square.py"])
    mocked_injecting_func.assert_called_once()
