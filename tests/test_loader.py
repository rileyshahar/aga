"""Tests for the `loader` module."""

from io import StringIO
from os.path import join as pathjoin
from pathlib import Path
from unittest.mock import patch

import pytest
from dill import dump  # type: ignore

from aga.core import Problem
from aga.loader import (
    NoMatchingSymbol,
    SubmissionSyntaxError,
    TooManyMatchingSymbols,
    load_problem,
    load_problems_from_path,
    load_script_from_path,
    load_symbol_from_path,
)


def car_tester(Car: type) -> None:  # pylint: disable=invalid-name
    """Test an imported Car class."""
    car = Car()
    car.drive(50)
    assert car.distance() == 50


def test_load_symbol_from_path_square(source_square: str) -> None:
    """Test that load_symbol_from_path loads a function."""

    square = load_symbol_from_path(source_square, "square")
    assert square(5) == 25


def test_load_symbol_from_path_car(source_car: str) -> None:
    """Test that load_symbol_from_path loads a class."""
    Car = load_symbol_from_path(source_car, "Car")  # pylint: disable=invalid-name
    car_tester(Car)


def test_load_symbol_from_path_invalid_source_errors(source_invalid: str) -> None:
    """Test that load_symbol_from_path errors on invalid source."""

    with pytest.raises(SubmissionSyntaxError):
        load_symbol_from_path(source_invalid, "foo")


def test_load_symbol_from_path_no_file_errors(tmp_path: Path) -> None:
    """Test that load_symbol_from_path errors on nonexistent files."""
    with pytest.raises(FileNotFoundError):
        load_symbol_from_path(str(tmp_path.joinpath("src.py")), "foo")


def test_load_symbol_from_path_no_symbol_errors(source_square: str) -> None:
    """Test that load_symbol_from_path errors on nonexistent symbols."""
    with pytest.raises(NoMatchingSymbol):
        load_symbol_from_path(source_square, "foo")


def test_load_symbol_from_dir_function(source_dir: str) -> None:
    """Test that load_symbol_from_path loads a function."""
    square = load_symbol_from_path(source_dir, "square")
    assert square(5) == 25


def test_load_symbol_from_dir_class(source_dir: str) -> None:
    """Test that load_symbol_from_path loads a class."""
    Car = load_symbol_from_path(source_dir, "Car")  # pylint: disable=invalid-name
    car_tester(Car)


def test_load_symbol_from_dir_nonexistent_symbol_errors(source_dir: str) -> None:
    """Test that load_symbol_from_path errors on nonexistent symbols."""
    with pytest.raises(NoMatchingSymbol):
        load_symbol_from_path(source_dir, "foo")


def test_load_symbol_from_dir_multiple_symble_errors(source_dir: str) -> None:
    """Test that load_symbol_from_path errors on nonexistent symbols."""
    with pytest.raises(TooManyMatchingSymbols):
        load_symbol_from_path(source_dir, "duplicate")


def test_load_problem(tmp_path: str, square: Problem[int]) -> None:
    """Test that load_problem loads square correctly."""

    path = pathjoin(tmp_path, "problem.pckl")
    with open(path, "wb") as file:
        dump(square, file)

    square_loaded: Problem[int] = load_problem(tmp_path, "problem.pckl")
    square_loaded.check()  # pylint: disable=no-member


def test_load_problems(source_square_problem: str) -> None:
    """Test that load_problem loads square correctly."""

    square_loaded: list[Problem[int]] = list(
        load_problems_from_path(source_square_problem)
    )
    square_loaded[0].check()  # pylint: disable=no-member


def test_load_script(source_hello_world_script: str) -> None:
    """Test that load_script works correctly."""

    script = load_script_from_path(source_hello_world_script)

    with patch("sys.stdout", new_callable=StringIO) as stdout:
        script()

    assert stdout.getvalue() == "Hello, world!\n"
