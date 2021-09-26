"""Contains the command-line interface."""

from typing import Iterable, Tuple

import typer

from .core import Output, Problem
from .gradescope import into_gradescope_zip
from .loader import NoMatchingSymbol, TooManyMatchingSymbols, load_symbol_from_dir

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


def _gen_gradescope(problem: Problem[Output]) -> None:
    """Generate a Gradescope autograder zip."""
    zip_path = into_gradescope_zip(problem)
    typer.echo(zip_path)


def _load_problem(problem: str) -> Problem[Output]:
    """Load a problem from the top-level directory."""
    try:
        return load_symbol_from_dir(".", problem)  # type: ignore

    except NoMatchingSymbol as err:
        typer.echo(f"problem not found: {problem}", err=True)
        raise typer.Exit(1) from err
    except TooManyMatchingSymbols as err:
        typer.echo(f"multiple matching problems: {problem}", err=True)
        raise typer.Exit(1) from err


# def _process_frontend(frontend: str) -> None:
#     if frontend not in (f[0] for f in FRONTENDS):
#         _handle_invalid_frontend(frontend)


def _handle_invalid_frontend(frontend: str) -> None:
    """Error on an invalid frontend."""
    typer.echo(f"invalid frontend: {frontend}", err=True)
    raise typer.Exit(1)


@app.command()
def gen(
    problem_name: str,
    frontend: str = typer.Option("gradescope", autocompletion=complete_frontend),
) -> None:
    """Generate an autograder file for a problem."""
    problem = _load_problem(problem_name)  # type: ignore

    if frontend == "gradescope":
        _gen_gradescope(problem)
    else:
        _handle_invalid_frontend(frontend)


@app.command()
def check(
    problem_name: str,
) -> None:
    """Generate an autograder file for a problem."""
    problem = _load_problem(problem_name)  # type: ignore

    try:
        problem.run_golden_tests()
    except AssertionError as err:
        typer.echo(f"{problem.name()} failed some golden tests: {err}", err=True)
        raise typer.Exit(1) from err
    else:
        typer.echo(f"{problem.name()} passed golden tests.")
        raise typer.Exit()
