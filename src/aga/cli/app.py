"""The main command-line typer application."""

from typing import Iterable, Optional, Tuple

import typer

from ..config import AgaConfig, load_config_from_path
from ..core import Output, Problem
from ..gradescope import into_gradescope_zip
from ..loader import NoMatchingSymbol, TooManyMatchingSymbols, load_symbol_from_dir

aga_app = typer.Typer()

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


def _gen_gradescope(problem: Problem[Output], path: Optional[str] = None) -> None:
    """Generate a Gradescope autograder zip."""
    zip_path = into_gradescope_zip(problem, path=path)
    typer.echo(zip_path)


def _load_config(path: str = "aga.toml") -> AgaConfig:
    """Load a config file from path, or return the default."""
    try:
        config = load_config_from_path(path)
    except FileNotFoundError:
        config = AgaConfig()

    return config


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


# def _process_frontend(frontend: str) -> None:
#     if frontend not in (f[0] for f in FRONTENDS):
#         _handle_invalid_frontend(frontend)


def _handle_invalid_frontend(frontend: str) -> None:
    """Error on an invalid frontend."""
    typer.echo(f"invalid frontend: {frontend}", err=True)
    raise typer.Exit(1)


@aga_app.command()
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
        _gen_gradescope(problem, output)
    else:
        _handle_invalid_frontend(frontend)


@aga_app.command()
def check(
    problem_name: str = typer.Argument(
        ..., help='The problem to check (see "problem discovery" in the CLI docs).'
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


click_object = typer.main.get_command(aga_app)  # exposed for documentation
