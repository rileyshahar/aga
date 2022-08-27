"""Contains various fixtures, especially pre-written problems."""

import sys
from datetime import timedelta
from importlib.resources import files
from os.path import join as pathjoin
from pathlib import Path
from shutil import copyfileobj
from typing import Iterable, Iterator, List

import pytest
from _pytest.config import Config
from pytest_lazyfixture import lazy_fixture  # type: ignore

from aga import group, problem, test_case, test_cases
from aga.config import AgaConfig, load_config_from_path
from aga.core import Problem, SubmissionMetadata

SOURCES = {
    "square_problem": """
from aga import problem, test_case

@test_case(2)
@problem()
def square(x: int) -> int:
    return x * x
""",
    "square": """
def square(x: int) -> int:
    return x * x
""",
    "square_incorrect": """
def square(x: int) -> int:
    return x - x
""",
    "square_error": """
def square(x: int) -> int:
    return x - y
""",
    "square_wrong_on_zero": """
def square(x: int) -> int:
    if x == 0:
        return 1
    return x * x
""",
    "duplicate": """
def duplicate(x: int):
    return (x, x)
""",
    "car": """
class Car:
    def __init__(self):
        self._distance = 0

    def drive(self, distance: int):
        self._distance += distance

    def distance(self) -> int:
        return self._distance
""",
    "str_len": """
def str_len(s: str) -> int:
    return len(s)
""",
    "invalid": """
This is not valid python code!
""",
    "diff": """
def difference(x: int, y: int = 0) -> int:
    return x - y
""",
    "hello_world": """
def hello_world() -> None:
    print("Hello, world!")
""",
    "hello_world_incorrect": """
def hello_world() -> None:
    print("hello, world.")
""",
    "hello_world_script": 'print("Hello, world!")',
    "hello_name": """
listener = input("Listener? ")
print(f"Hello, {listener}.")

speaker = input("Speaker? ")
print(f"I'm {speaker}.")
""",
    "hello_name_incorrect": """
listener = input("Listener? ")
speaker = input("Speaker? ")

print(f"Hello, {speaker}.")
print(f"I'm {listener}.")
""",
}


def _write_source_to_file(path: Path, source: str) -> str:
    """Write source code to a file, returning a string of its path."""
    with open(path, "w", encoding="UTF-8") as file:
        file.write(source)

    return str(path)


def _make_source_fixture(source: str, name: str) -> None:
    @pytest.fixture(name="source_" + name)
    def inner(tmp_path: Path) -> str:
        """Generate a source file, returning its path."""
        return _write_source_to_file(tmp_path.joinpath("src.py"), source)

    module = sys.modules[__name__]
    setattr(module, name, inner)


for (_name, _source) in SOURCES.items():
    _make_source_fixture(_source, _name)


def _write_sources_to_files(
    path: Path, sources: Iterable[str], filenames: Iterable[str]
) -> str:
    """Write a series of source files to files in path, returning the directory path."""
    for source, file in zip(sources, filenames):
        _write_source_to_file(path.joinpath(file), source)

    return str(path)


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
        (
            SOURCES["car"],
            SOURCES["invalid"],
            SOURCES["square"],
            SOURCES["duplicate"],
            SOURCES["duplicate"],
        ),
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
        lazy_fixture("square_custom_name"),
        lazy_fixture("times"),
        lazy_fixture("diff"),
        lazy_fixture("palindrome"),
        lazy_fixture("kwd"),
        lazy_fixture("pos_and_kwd"),
        lazy_fixture("str_len"),
        lazy_fixture("square_simple_weighted"),
        lazy_fixture("square_grouped"),
        lazy_fixture("square_generated_cases"),
        lazy_fixture("diff_generated"),
        lazy_fixture("pos_and_kwd_generated"),
        lazy_fixture("pos_and_kwd_zip"),
        lazy_fixture("pos_and_kwd_generator_function"),
        lazy_fixture("hello_world"),
        lazy_fixture("hello_name"),
    ]
)
def valid_problem(request):
    """Generate a parameterized test over a number of guaranteed-valid Problems."""
    return request.param


@pytest.fixture(name="square")
def fixture_square() -> Problem[int]:
    """Generate a problem which tests a square function."""

    @test_case(4)
    @test_case(2, aga_expect=4)
    @test_case(-2, aga_expect=4, aga_hidden=True)
    @problem()
    def square(x: int) -> int:
        """Square x."""
        return x * x

    return square


@pytest.fixture(name="square_custom_name")
def fixture_square_custom_name() -> Problem[int]:
    """Generate a problem which tests a square function.

    This fixture uses the `aga_name` argument to `test_case` to generate a test case
    with a name different from the default.
    """

    @test_case(4, aga_name="This is a deliberately silly name!")
    @test_case(2, aga_expect=4, aga_name="Test positive two.")
    @test_case(-2, aga_expect=4, aga_hidden=True, aga_name="Test minus two.")
    @problem()
    def square(x: int) -> int:
        """Square x."""
        return x * x

    return square


@pytest.fixture(name="times")
def fixture_times() -> Problem[int]:
    """Generate a problem which tests a times function."""

    @test_case(4, 6)
    @test_case(-2, 16)
    @test_case(2, -3, aga_hidden=True, aga_expect=-6)
    @problem()
    def times(x: int, y: int) -> int:
        """Compute x * y."""
        return x * y

    return times


@pytest.fixture(name="diff")
def fixture_diff() -> Problem[int]:
    """Generate a problem which tests a difference function."""

    @test_case(17, 10)
    @test_case(2, 4, aga_expect=-2)
    @test_case(3, 1, aga_expect=2)
    @problem()
    def difference(x: int, y: int) -> int:
        """Compute x - y."""
        return x - y

    return difference


@pytest.fixture(name="str_len")
def fixture_str_len() -> Problem[int]:
    """Generate a problem which tests a str length function."""

    @test_case("hello, world")
    @test_case("", aga_expect=0)
    @test_case("noether", aga_expect=7)
    @test_case("14", aga_expect=2)
    @problem()
    def str_len(s: str) -> int:
        """Find the length of s."""
        return len(s)

    return str_len


@pytest.fixture(name="palindrome")
def fixture_palindrome() -> Problem[bool]:
    """Generate a problem which tests a string palindrome function.

    This problem uses the `name` argument to `problem` to declare a different name from
    the function it decorates.
    """

    @test_case("eve")
    @test_case("hello")
    @test_case("", aga_expect=True)
    @test_case("goodbye", aga_expect=False)
    @test_case("123454321", aga_expect=True)
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
    @test_case(aga_expect="")
    @test_case(s="goodbye", aga_expect="goodbye")
    @test_case(s="123454321", aga_expect="123454321")
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
    @test_case(4, aga_expect=4)
    @test_case(2, y=4, aga_expect=-2)
    @test_case(3, y=1, aga_expect=2)
    @problem()
    def difference(x: int, y: int = 0) -> int:
        """Compute x - y."""
        return x - y

    return difference


@pytest.fixture(name="diff_bad_gt")
def fixture_diff_bad_gt(diff: Problem[int]) -> Problem[int]:
    """Generate an implementation of difference with an incorrect golden test."""
    return test_case(3, 1, aga_expect=1)(diff)


@pytest.fixture(name="diff_bad_impl")
def fixture_diff_bad_impl() -> Problem[int]:
    """Generate a difference problem with an incorrect implementation."""

    @test_case(17, 10)
    @test_case(2, 4, aga_expect=-2)
    @test_case(3, 1, aga_expect=2)
    @problem()
    def diff_should_fail(x: int, y: int) -> int:
        """Compute x - y."""
        return x + y

    return diff_should_fail


@pytest.fixture(name="square_simple_weighted")
def fixture_square_simple_weighted() -> Problem[int]:
    """Generate a problem which tests a square function, with simple manual weights."""

    @test_case(-2, aga_weight=2)
    @test_case(-1, aga_weight=0, aga_value=2.0)
    @test_case(0, aga_weight=2, aga_value=4.0)
    @test_case(1, aga_value=2.0)
    @test_case(2)
    @problem()
    def square(x: int) -> int:
        """Square x."""
        return x * x

    return square


@pytest.fixture(name="square_grouped")
def fixture_square_grouped() -> Problem[int]:
    """Generate a problem which tests a square function, with grouped weights."""
    # problem has score 20
    # groups get assigned scores 6, 12, 2
    # negative group, score 6, -1 gets score 3.333, -2 gets score 2.666
    # 0 group just gets 12
    # positive group, 1 gets score 2, 2 gets score 0

    @test_case(-2, aga_weight=2)
    @test_case(-1, aga_weight=1, aga_value=2.0)
    @group(weight=2)
    @test_case(0, aga_weight=2, aga_value=4.0)
    @group(weight=0, value=2.0)
    @test_case(1, aga_value=2.0)
    @test_case(2)
    @problem()
    def square(x: int) -> int:
        """Square x."""
        return x * x

    return square


@pytest.fixture(name="square_generated_cases")
def fixture_square_generated_cases() -> Problem[int]:
    """Generate a problem which tests a square function using generated test cases."""

    @test_cases(range(-2, 3))
    @problem()
    def square(x: int) -> int:
        """Square x."""
        return x * x

    return square


@pytest.fixture(name="diff_generated")
def fixture_diff_generator() -> Problem[int]:
    """Generate a problem which tests a diff function.

    This function has generator-created test cases for two positional arguments.
    """

    @test_cases(range(-1, 2), range(-1, 2))
    @problem()
    def difference(x: int, y: int) -> int:
        """Compute x - y."""
        return x - y

    return difference


@pytest.fixture(name="pos_and_kwd_generated")
def fixture_pos_and_kwd_generated() -> Problem[int]:
    """Generate a problem which tests a diff function.

    This function has generator-created test cases for both positional and keyword
    arguments.
    """

    @test_cases(range(-1, 2), y=range(-1, 2))
    @problem()
    def difference(x: int, y: int = 0) -> int:
        """Compute x - y."""
        return x - y

    return difference


@pytest.fixture(name="pos_and_kwd_zip")
def fixture_pos_and_kwd_zip() -> Problem[int]:
    """Generate a problem which tests a diff function.

    This function has generator-created test cases for both positional and keyword
    arguments.
    """

    @test_cases([-1, 0, 1], y=range(-1, 2), aga_product=False)
    @problem()
    def difference(x: int, y: int = 0) -> int:
        """Compute x - y."""
        return x - y

    return difference


@pytest.fixture(name="pos_and_kwd_generator_function")
def fixture_pos_and_kwd_generator_function() -> Problem[int]:
    """Generate a problem which tests a diff function.

    This function has generator-created test cases for both positional and keyword
    arguments.
    """

    def generator() -> Iterator[int]:
        for i in range(-1, 2):
            yield i

    @test_cases(generator(), y=generator())
    @problem()
    def difference(x: int, y: int = 0) -> int:
        """Compute x - y."""
        return x - y

    return difference


@pytest.fixture(name="hello_world")
def fixture_hello_world() -> Problem[None]:
    """Generate a problem which tests stdout."""

    @test_case()
    @problem(check_stdout=True)
    def hello_world() -> None:
        """Print 'Hello, world!'."""
        print("Hello, world!")

    return hello_world


@pytest.fixture(name="hello_world_script")
def fixture_hello_world_script() -> Problem[None]:
    """Generate a problem which tests a hello world script."""

    @test_case()
    @problem(script=True)
    def hello_world() -> None:
        """Print 'Hello, world!'."""
        print("Hello, world!")

    return hello_world


@pytest.fixture(name="hello_name")
def fixture_hello_name() -> Problem[None]:
    """Generate a problem which tests a script with input."""

    @test_case("Alice", "Bob")
    @test_case("world", "me")
    @problem(script=True)
    def hello_name() -> None:
        """Print 'Hello, world!'."""
        listener = input("Listener? ")
        print(f"Hello, {listener}.")

        speaker = input("Speaker ?")
        print(f"I'm {speaker}.")

    return hello_name


@pytest.fixture(name="example_config_file")
def fixture_example_config_file(
    tmp_path: Path,
) -> str:
    """Get a path to the example config file."""
    path = pathjoin(tmp_path, "aga.toml")

    with files("tests.resources").joinpath("aga.toml").open() as src:  # type: ignore
        with open(path, "w", encoding="UTF-8") as dest:
            copyfileobj(src, dest)

    return path


@pytest.fixture(name="example_config")
def fixture_example_config(
    example_config_file: str,
) -> AgaConfig:
    """Get the example metadata file from the gradescope documentation."""
    return load_config_from_path(example_config_file)


@pytest.fixture(name="metadata")
def fixture_metadata() -> SubmissionMetadata:
    """Get the example metadata file from the gradescope documentation."""
    return SubmissionMetadata(total_score=20.0, time_since_due=timedelta())
