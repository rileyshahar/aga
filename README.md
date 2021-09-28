# aga

[![Tests](https://github.com/nihilistkitten/aga/workflows/Tests/badge.svg)](https://github.com/nihilistkitten/aga/actions?workflow=Tests) [![Codecov](https://codecov.io/gh/nihilistkitten/aga/branch/main/graph/badge.svg)](https://codecov.io/gh/nihilistkitten/aga) [![PyPI](https://img.shields.io/pypi/v/aga.svg)](https://pypi.org/project/aga/) [![Read the Docs](https://readthedocs.org/projects/aga/badge/)](https://aga.readthedocs.io/)

**aga** (aga grades assignments) is a tool for easily producing autograders for python programming assignments.

## Installation

Install from pip:

```bash
pip install aga
```

## Quickstart

In `square.py` (or any python file), write:

```python
from aga import problem, test_case


@test_case(-3)
@test_case(100)
@test_case(2, aga_output=4)
@test_case(-2, aga_output=4)
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

Then run `aga gen square` from the directory with `square.py`. This will generate a ZIP file suitable for upload to gradescope.

## Usage

Aga relies on the notion of a _golden solution_ to a given problem which is known to be correct. The main work of the library is to compare the output of this golden solution on some family of test inputs against the output of a student submission. To that end, aga integrates with frontends: existing classroom software which allow submission of student code. Currently, only gradescope is supported.

To use aga:

1. Write a golden solution to some programming problem.
2. Decorate this solution with the `problem` decorator.
3. Decorate this problem with any number of `test_case` decorators, which take arbitrary positional or keyword arguments and pass them verbatim to the golden and submitted functions.
4. Generate the autograder using the CLI: `aga gen <function_name>`.

The `test_case` decorator may optionally take a special keyword argument called `aga_output`. This allows easy testing of the golden solution: aga will not successfully produce an autograder unless the golden solution's output matches the `aga_output`. You should use these as sanity checks to ensure your golden solution is implemented correctly.

For complete documentation, including configuring problem and test case metadata, see the [API reference](https://aga.readthedocs.io/en/stable/reference.html).

For CLI documentation, run `aga --help`, or access the docs [online](https://aga.readthedocs.io/en/stable/cli.html).

## Contributing

Bug reports, feature requests, and pull requests are all welcome. For details on our test suite, development environment, and more, see the [developer documentation](https://aga.readthedocs.io/en/stable/development.html).
