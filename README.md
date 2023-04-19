<div align="center">

# aga grades assignments

[![tests](https://github.com/nihilistkitten/aga/workflows/tests/badge.svg)](https://github.com/nihilistkitten/aga/actions?workflow=tests)
[![lints](https://github.com/nihilistkitten/aga/workflows/lints/badge.svg)](https://github.com/nihilistkitten/aga/actions?workflow=lints)
[![Codecov](https://codecov.io/gh/nihilistkitten/aga/branch/main/graph/badge.svg)](https://codecov.io/gh/nihilistkitten/aga)
[![PyPI](https://img.shields.io/pypi/v/aga.svg)](https://pypi.org/project/aga/)
[![Read the Docs](https://readthedocs.org/projects/aga/badge/)](https://aga.readthedocs.io/)
[![License](https://img.shields.io/github/license/nihilistkitten/aga)](https://choosealicense.com/licenses/mit/)

</div>

**aga** (**a**ga **g**rades **a**ssignments) is a tool for easily producing autograders for python programming assignments, originally developed for Reed College's CS1 course.

## Motivation

Unlike traditional software testing, where there is likely no _a priori_ known-correct implementation, there is always such an implementation (or one can be easily written by course staff) in homework grading. Therefore, applying traditional software testing frameworks to homework grading is limited. Relying on reference implementations (what aga calls _golden solutions_) has several benefits:

1. Reliability: having a reference solution gives a second layer of confirmation for the correctness of expected outputs. Aga supports _golden tests_, which function as traditional unit tests of the golden solution.
2. Test case generation: many complex test cases can easily be generated via the reference solution, instead of needing to work out the expected output by hand. Aga supports generating test cases from inputs without explcitly referring to an expected output, and supports collecting test cases from python generators.
3. Property testing: unit testing libraries like [hypothesis](https://hypothesis.readthedocs.io) allow testing large sets of arbitrary inputs for certain properties, and identifying simple inputs which reproduce violations of those properties. This is traditionally unreliable, because identifying specific properties to test is difficult. In homework grading, the property can simply be "the input matches the golden solution's output." Support for hypothesis is a [long-term goal](https://github.com/nihilistkitten/aga/issues/32) of aga.

## Installation

Install from pip:

```bash
pip install aga
```

or with the python dependency manager of your choice (I like [poetry](https://github.com/python-poetry/poetry)), for example:

```bash
curl -sSL https://install.python-poetry.org | python3 -
echo "cd into aga repo"
cd aga
poetry install && poetry shell
```

## Example

In `square.py` (or any python file), write:

```python
from aga import problem, test_case, test_cases

@test_cases(-3, 100)
@test_case(2, aga_expect=4)
@test_case(-2, aga_expect=4)
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

Then run `aga gen square.py` from the directory with `square.py`. This will generate a ZIP file suitable for upload to Gradescope.

## Usage

Aga relies on the notion of a _golden solution_ to a given problem which is known to be correct. The main work of the library is to compare the output of this golden solution on some family of test inputs against the output of a student submission. To that end, aga integrates with frontends: existing classroom software which allow submission of student code. Currently, only Gradescope is supported.

To use aga:

1. Write a golden solution to some programming problem.
2. Decorate this solution with the `problem` decorator.
3. Decorate this problem with any number of `test_case` decorators, which take arbitrary positional or keyword arguments and pass them verbatim to the golden and submitted functions.
4. Generate the autograder using the CLI: `aga gen <file_name>`.

The `test_case` decorator may optionally take a special keyword argument called `aga_expect`. This allows easy testing of the golden solution: aga will not successfully produce an autograder unless the golden solution's output matches the `aga_expect`. You should use these as sanity checks to ensure your golden solution is implemented correctly.

For more info, see the [tutorial](https://aga.readthedocs.io/en/stable/tutorial.html).

For complete documentation, including configuring problem and test case metadata, see the [API reference](https://aga.readthedocs.io/en/stable/reference.html).

For CLI documentation, run `aga --help`, or access the docs [online](https://aga.readthedocs.io/en/stable/cli.html).

## Contributing

Bug reports, feature requests, and pull requests are all welcome. For details on our test suite, development environment, and more, see the [developer documentation](https://aga.readthedocs.io/en/stable/development.html).

<!-- vim:set tw=0: -->
