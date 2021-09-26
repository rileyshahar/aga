"""Tests for the `loader` module."""

from os.path import join as pathjoin
from pathlib import Path
from typing import Iterable

import pytest
from dill import dump  # type: ignore

from aga import Problem
from aga.loader import (
    NoMatchingSymbol,
    SubmissionSyntaxError,
    TooManyMatchingSymbols,
    load_problem,
    load_symbol_from_dir,
    load_symbol_from_path,
)

SOURCE_SQUARE = """
def square(x: int) -> int:
    return x * x
"""

SOURCE_DUPLICATE = """
def duplicate(x: int):
    return (x, x)
"""

SOURCE_CAR = """
class Car:
    def __init__(self):
        self._distance = 0

    def drive(self, distance: int):
        self._distance += distance

    def distance(self) -> int:
        return self._distance
"""

SOURCE_INVALID = """
This is not valid python code!
"""


def _write_source_to_file(path: Path, source: str) -> str:
    """Write source code to a file, returning a string of its path."""
    with open(path, "w", encoding="UTF-8") as file:
        file.write(source)

    return str(path)


def _write_sources_to_files(
    path: Path, sources: Iterable[str], filenames: Iterable[str]
) -> str:
    """Write a series of source files to files in path, returning the directory path."""
    for source, file in zip(sources, filenames):
        _write_source_to_file(path.joinpath(file), source)

    return str(path)


@pytest.fixture(name="source_square")
def fixture_source_square(tmp_path: Path) -> str:
    """Generate a source file with SOURCE_SQUARE, returning its path."""
    return _write_source_to_file(tmp_path.joinpath("src.py"), SOURCE_SQUARE)


@pytest.fixture(name="source_dir")
def fixture_source_dir(tmp_path: Path) -> str:
    """Generate a directory containing numerous valid and invalid source files.

    The directory contains:
    - invalid.txt, an invalid python file.
    - square.py, which contains a `square` function.
    - car.py, which contains a `Car` class and may be tested by `car_tester`.
    - duplicate-one.py, which contains a `duplicate` function.
    - duplicate-two.py, which contains a `duplicate` function.
    """
    return _write_sources_to_files(
        tmp_path,
        (SOURCE_CAR, SOURCE_INVALID, SOURCE_SQUARE, SOURCE_DUPLICATE, SOURCE_DUPLICATE),
        ("car.py", "invalid.txt", "square.py", "duplicate-one.py", "duplicate-two.py"),
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


def test_load_symbol_from_path_car(tmp_path: Path) -> None:
    """Test that load_symbol_from_path loads a class."""
    path = _write_source_to_file(tmp_path.joinpath("src.py"), SOURCE_CAR)

    Car = load_symbol_from_path(path, "Car")  # pylint: disable=invalid-name
    car_tester(Car)


def test_load_symbol_from_path_invalid_source_errors(tmp_path: Path) -> None:
    """Test that load_symbol_from_path errors on invalid source."""
    path = _write_source_to_file(tmp_path.joinpath("src.py"), SOURCE_INVALID)

    with pytest.raises(SubmissionSyntaxError):
        load_symbol_from_path(path, "foo")


def test_load_symbol_from_path_no_file_errors(tmp_path: Path) -> None:
    """Test that load_symbol_from_path errors on nonexistent files."""
    with pytest.raises(FileNotFoundError):
        load_symbol_from_path(str(tmp_path.joinpath("src.py")), "foo")


def test_load_symbol_from_path_no_symbol_errors(source_square: str) -> None:
    """Test that load_symbol_from_path errors on nonexistent symbols."""
    with pytest.raises(NoMatchingSymbol):
        load_symbol_from_path(source_square, "foo")


def test_load_symbol_from_dir_function(source_dir: str) -> None:
    """Test that load_symbol_from_dir loads a function."""
    square = load_symbol_from_dir(source_dir, "square")
    assert square(5) == 25


def test_load_symbol_from_dir_class(source_dir: str) -> None:
    """Test that load_symbol_from_dir loads a class."""
    Car = load_symbol_from_dir(source_dir, "Car")  # pylint: disable=invalid-name
    car_tester(Car)


def test_load_symbol_from_dir_nonexistent_symbol_errors(source_dir: str) -> None:
    """Test that load_symbol_from_dir errors on nonexistent symbols."""
    with pytest.raises(NoMatchingSymbol):
        load_symbol_from_dir(source_dir, "foo")


def test_load_symbol_from_dir_multiple_symble_errors(source_dir: str) -> None:
    """Test that load_symbol_from_dir errors on nonexistent symbols."""
    with pytest.raises(TooManyMatchingSymbols):
        load_symbol_from_dir(source_dir, "duplicate")


def test_load_problem(tmp_path: str, square: Problem[int]) -> None:
    """Test that load_problem loads square correctly."""

    path = pathjoin(tmp_path, "problem.pckl")
    with open(path, "wb") as file:
        dump(square, file)

    square_loaded: Problem[int] = load_problem(tmp_path, "problem.pckl")
    square_loaded.run_golden_tests()  # pylint: disable=no-member
