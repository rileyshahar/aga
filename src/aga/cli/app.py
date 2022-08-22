"""The main command-line typer application."""

from os.path import basename, splitext
from typing import Any, Iterable, Optional, Tuple
from unittest import TextTestRunner

import typer

from ..config import AgaConfig, load_config_from_path
from ..core import Output, Problem
from ..gradescope import into_gradescope_zip
from ..loader import (
    NoMatchingSymbol,
    TooManyMatchingSymbols,
    load_problems_from_path,
    load_symbol_from_dir,
    load_symbol_from_path,
)

app = typer.Typer()

FRONTENDS = (
    (
        "gradescope",
        "generate a gradescope autograder zip",
    ),
)


def complete_frontend(incomplete: str) -> Iterable[Tuple[str, str]]:
    """Autocomplete a frontend."""
    for frontend in FRONTENDS:
        if frontend[0].startswith(incomplete):
            yield frontend


def _zip_prefix(path: str) -> str:
    """Determine the prefix of the zip file created from the problems at path."""
    return splitext(basename(path))[1]  # type: ignore


def _gen_gradescope(
    name: str, problems: list[Problem[Output]], path: Optional[str] = None
) -> None:
    """Generate a Gradescope autograder zip."""
    zip_path = into_gradescope_zip(name, problems, path=path)
    typer.echo(zip_path)


def _load_config(path: str = "aga.toml") -> AgaConfig:
    """Load a config file from path, or return the default."""
    try:
        config = load_config_from_path(path)
    except FileNotFoundError:
        config = AgaConfig()

    return config


def _load_problems(path: str, config: AgaConfig) -> list[Problem[Any]]:
    """Load a problem from the top-level directory."""
    problems = list(load_problems_from_path(path))
    if not problems:
        typer.echo(f"no problems found at {path}", err=True)
        raise typer.Exit(1)

    for problem in problems:
        problem.update_config_weak(config)

    return problems


def _load_problem(name: str, config: AgaConfig) -> Problem[Output]:
    """Load a problem from the top-level directory."""
    try:
        problem = load_symbol_from_dir(".", name)  # type: Problem[Output]
        problem.update_config_weak(config)
        return problem

    except NoMatchingSymbol as err:
        typer.echo(f"problem not found: {name}", err=True)
        raise typer.Exit(1) from err
    except TooManyMatchingSymbols as err:
        typer.echo(f"multiple matching problems: {name}", err=True)
        raise typer.Exit(1) from err


def _handle_invalid_frontend(frontend: str) -> None:
    """Error on an invalid frontend."""
    typer.echo(f"invalid frontend: {frontend}", err=True)
    raise typer.Exit(1)


@app.command()
def gen_many(
    source: str = typer.Argument(
        ...,
        help="The problem file to generate.",
    ),
    frontend: str = typer.Option(
        "gradescope",
        "-f",
        "--frontend",
        autocompletion=complete_frontend,
        help="The frontend to use. Currently only gradescope is supported.",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="The path to place the output file(s).",
    ),
    config_file: str = typer.Option(
        "aga.toml", "--config", "-c", help="The path to the aga config file."
    ),
) -> None:
    """Generate an autograder file for a problem."""
    config = _load_config(config_file)
    problem = _load_problems(source, config)  # type: ignore

    if frontend == "gradescope":
        _gen_gradescope(_zip_prefix(source), problem, output)
    else:
        _handle_invalid_frontend(frontend)


@app.command()
def gen(
    problem_name: str = typer.Argument(
        ..., help='The problem to generate (see "problem discovery" in the CLI docs).'
    ),
    frontend: str = typer.Option(
        "gradescope",
        "-f",
        "--frontend",
        autocompletion=complete_frontend,
        help="The frontend to use. Currently only gradescope is supported.",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="The path to place the output file(s).",
    ),
    config_file: str = typer.Option(
        "aga.toml", "--config", "-c", help="The path to the aga config file."
    ),
) -> None:
    """Generate an autograder file for a problem."""
    config = _load_config(config_file)
    problem = _load_problem(problem_name, config)  # type: ignore

    if frontend == "gradescope":
        _gen_gradescope(problem_name, [problem], output)
    else:
        _handle_invalid_frontend(frontend)


@app.command()
def check(
    problem_name: str = typer.Argument(
        ...,
        metavar="problem",
        help='The problem to check (see "problem discovery" in the CLI docs).',
    ),
    config_file: str = typer.Option(
        "aga.toml", "--config", "-c", help="The path to the aga config file."
    ),
) -> None:
    """Check a problem against test cases with an `aga_expect`."""
    config = _load_config(config_file)
    problem = _load_problem(problem_name, config)  # type: ignore

    try:
        problem.check()
    except AssertionError as err:
        typer.echo(f"{problem.name()} failed some golden tests: {err}", err=True)
        raise typer.Exit(1) from err
    else:
        typer.echo(f"{problem.name()} passed golden tests.")
        raise typer.Exit()


@app.command()
def run(
    problem_name: str = typer.Argument(
        ...,
        metavar="problem",
        help='The problem to check (see "problem discovery" in the CLI docs).',
    ),
    submission_file: str = typer.Argument(
        ..., help="The file containing the student submission."
    ),
    config_file: str = typer.Option(
        "aga.toml", "--config", "-c", help="The path to the aga config file."
    ),
) -> None:
    """Run the autograder on an example submission."""
    config = _load_config(config_file)
    problem: Problem = _load_problem(problem_name, config)  # type: ignore
    under_test = load_symbol_from_path(submission_file, problem.expected_symbol())

    suite = problem.generate_test_suite(under_test, 1.0)
    TextTestRunner().run(suite)


click_object = typer.main.get_command(app)  # exposed for documentation
