"""Tests for the command-line interfact."""

from typing import TypeVar
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from aga.cli import FRONTENDS, app, complete_frontend
from aga.core import Problem
from aga.loader import NoMatchingSymbol, TooManyMatchingSymbols

Output = TypeVar("Output")

runner = CliRunner(mix_stderr=False)


@pytest.fixture(name="mocked_lsfd")
def fixture_mocked_lsfd(mocker: MockerFixture) -> MagicMock:
    """Generate a mocked `load_symbol_from_dir`."""
    return mocker.patch("aga.cli.load_symbol_from_dir")


@pytest.fixture(name="mocked_igz")
def fixture_mocked_igz(mocker: MockerFixture) -> MagicMock:
    """Generate a mocked `into_gradescope_zip`."""
    return mocker.patch("aga.cli.into_gradescope_zip")


def test_gen_gradescope(
    mocked_lsfd: MagicMock, mocked_igz: MagicMock, square: Problem[int]
) -> None:
    """Test that gen_gradescope works correctly."""
    mocked_lsfd.return_value = square
    mocked_igz.return_value = "square.zip"

    result = runner.invoke(app, ["gen", "square"])

    mocked_lsfd.assert_called_once()
    mocked_igz.assert_called_once()

    assert "square.zip" in result.stdout
    assert result.exit_code == 0


def test_gen_gradescope_no_match(mocked_lsfd: MagicMock, mocked_igz: MagicMock) -> None:
    """Test that gen_gradescope errors with no matching symbol."""
    mocked_lsfd.side_effect = NoMatchingSymbol
    result = runner.invoke(app, ["gen", "square"])

    mocked_lsfd.assert_called_once()
    mocked_igz.assert_not_called()

    assert "problem not found" in result.stderr
    assert result.exit_code == 1


def test_gen_gradescope_multiple_matches(
    mocked_lsfd: MagicMock, mocked_igz: MagicMock
) -> None:
    """Test that gen_gradescope errors with multiple matching symbols."""
    mocked_lsfd.side_effect = TooManyMatchingSymbols
    result = runner.invoke(app, ["gen", "square"])

    mocked_lsfd.assert_called_once()
    mocked_igz.assert_not_called()

    assert "multiple matching problems" in result.stderr
    assert result.exit_code == 1


def test_gen_invalid_frontend(mocked_lsfd: MagicMock, mocked_igz: MagicMock) -> None:
    """Test that gen_gradescope errors with multiple matching symbols."""
    result = runner.invoke(app, ["gen", "square", "--frontend", "doesnt-exist"])

    mocked_lsfd.assert_called_once()
    mocked_igz.assert_not_called()

    assert "invalid frontend" in result.stderr
    assert result.exit_code == 1


def test_check_valid_problem(
    mocked_lsfd: MagicMock, valid_problem: Problem[Output]
) -> None:
    """Test that check succeeds with a valid problem."""
    mocked_lsfd.return_value = valid_problem

    result = runner.invoke(app, ["check", valid_problem.name()])

    mocked_lsfd.assert_called_once()

    assert "passed golden tests" in result.stdout
    assert result.exit_code == 0


def test_check_invalid_problem(
    mocked_lsfd: MagicMock, diff_bad_gt: Problem[int]
) -> None:
    """Test that check fails with an invalid problem."""
    mocked_lsfd.return_value = diff_bad_gt

    result = runner.invoke(app, ["check", diff_bad_gt.name()])

    mocked_lsfd.assert_called_once()

    print(result.stdout)
    print(result.stderr)

    assert "failed some golden tests" in result.stderr
    assert result.exit_code == 1


def test_complete_frontend_empty() -> None:
    """Check that complete_frontend works with an empty string."""
    assert tuple(complete_frontend("")) == FRONTENDS


def test_complete_frontend_incomplete() -> None:
    """Check that complete_frontend works with an incomplete string."""
    assert tuple(complete_frontend("grade")) == FRONTENDS


def test_complete_frontend_no_match() -> None:
    """Check that complete_frontend works with a non-matching string."""
    assert not tuple(complete_frontend("nonexistent"))
