"""Contains various fixtures, especially pre-written problems."""

from pathlib import Path
from typing import Iterable, List

import pytest
from _pytest.config import Config
from pytest_lazyfixture import lazy_fixture  # type: ignore

from aga import problem, test_case
from aga.core import Problem

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


@pytest.fixture(name="source_car")
def fixture_source_car(tmp_path: Path) -> str:
    """Generate a source file with SOURCE_CAR, returning its path."""
    return _write_source_to_file(tmp_path.joinpath("src.py"), SOURCE_CAR)


@pytest.fixture(name="source_invalid")
def fixture_source_invalid(tmp_path: Path) -> str:
    """Generate a source file with SOURCE_INVALID, returning its path."""
    return _write_source_to_file(tmp_path.joinpath("src.py"), SOURCE_INVALID)


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


def pytest_collection_modifyitems(config: Config, items: List[pytest.Item]) -> None:
    """Prevent pytest from running `slow` tests unless `-m "slow"` is passed."""
    keywordexpr = config.option.keyword
    markexpr = config.option.markexpr
    if keywordexpr or markexpr:
        return

    skip_slow = pytest.mark.skip(reason="`-m slow` not selected")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(
    params=[  # type: ignore
        lazy_fixture("square"),
        lazy_fixture("diff"),
        lazy_fixture("palindrome"),
        lazy_fixture("kwd"),
        lazy_fixture("pos_and_kwd"),
    ]
)
def valid_problem(request):
    """Generate a parameterized test over a number of guaranteed-valid Problems."""
    return request.param


@pytest.fixture(name="square")
def fixture_square() -> Problem[int]:
    """Generate a problem which tests a square function."""

    @test_case(4)
    @test_case(2, aga_output=4)
    @test_case(-2, aga_output=4)
    @problem()
    def square(x: int) -> int:
        """Square x."""
        return x * x

    return square


@pytest.fixture(name="diff")
def fixture_diff() -> Problem[int]:
    """Generate a problem which tests a difference function."""

    @test_case(17, 10)
    @test_case(2, 4, aga_output=-2)
    @test_case(3, 1, aga_output=2)
    @problem()
    def difference(x: int, y: int) -> int:
        """Compute x - y."""
        return x - y

    return difference


@pytest.fixture(name="palindrome")
def fixture_palindrome() -> Problem[bool]:
    """Generate a problem which tests a string palindrome function.

    This problem uses the `name` argument to `problem` to declare a different name from
    the function it decorates.
    """

    @test_case("eve")
    @test_case("hello")
    @test_case("", aga_output=True)
    @test_case("goodbye", aga_output=False)
    @test_case("123454321", aga_output=True)
    @problem(name="palindrome")
    def strpal(s: str) -> bool:
        """Determine whether s is a palindrome."""
        return s == s[::-1]

    return strpal


@pytest.fixture(name="kwd")
def fixture_kwd() -> Problem[str]:
    """Generate a problem which tests a string identity function.

    The special part of this function is that it takes an argument via keyword arg, not
    positional arg.
    """

    @test_case(s="eve")
    @test_case(s="hello")
    @test_case(aga_output="")
    @test_case(s="goodbye", aga_output="goodbye")
    @test_case(s="123454321", aga_output="123454321")
    @problem()
    def kwd(s: str = "") -> str:
        """Return s."""
        return s

    return kwd


@pytest.fixture(name="pos_and_kwd")
def fixture_pos_and_kwd() -> Problem[int]:
    """Generate a problem which tests a diff function.

    The special part of this function is that it takes arguments via both positional and
    keyword args.
    """

    @test_case(-5)
    @test_case(17, y=10)
    @test_case(4, aga_output=4)
    @test_case(2, y=4, aga_output=-2)
    @test_case(3, y=1, aga_output=2)
    @problem()
    def difference(x: int, y: int = 0) -> int:
        """Compute x - y."""
        return x - y

    return difference


@pytest.fixture(name="diff_bad_gt")
def fixture_diff_bad_gt(diff: Problem[int]) -> Problem[int]:
    """Generate an implementation of difference with an incorrect golden test."""
    return test_case(3, 1, aga_output=1)(diff)


@pytest.fixture(name="diff_bad_impl")
def fixture_diff_bad_impl() -> Problem[int]:
    """Generate a difference problem with an incorrect implementation."""

    @test_case(17, 10)
    @test_case(2, 4, aga_output=-2)
    @test_case(3, 1, aga_output=2)
    @problem()
    def diff_should_fail(x: int, y: int) -> int:
        """Compute x - y."""
        return x + y

    return diff_should_fail
