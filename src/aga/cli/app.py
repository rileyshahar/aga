"""The main command-line typer application."""
import pathlib
from datetime import datetime
from typing import Iterable, Optional, Tuple, List, Any

import typer

from ..config import AgaConfig, load_config_from_path
from ..core import Problem, SubmissionMetadata
from ..gradescope import into_gradescope_zip
from ..loader import load_problems_from_path
from ..runner import load_and_run
from .ui import print_fancy_summary

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


def _gen_gradescope(problem: Problem[Any, Any], path: Optional[str] = None) -> None:
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


def _load_injection_config(
    config: AgaConfig,
    injected_files: Iterable[pathlib.Path],
    injected_dirs: Iterable[pathlib.Path],
    injection_module: str,
    auto_inject: bool,
) -> AgaConfig:
    """Load injected files and directories into the config."""
    config.injection.update(fls=injected_files, dirs=injected_dirs)

    if auto_inject:
        config.injection.find_auto_injection()

    if not config.injection.is_valid:
        raise ValueError("injection files or dirs are invalid")

    config.injection.create_injection_module(injection_module)
    config.injection.inject()

    return config


def _load_problem(path: str, config: AgaConfig) -> Problem[Any, Any]:
    """Load a problem from the top-level directory."""
    problems = list(load_problems_from_path(path))

    if not problems:
        typer.echo(f"No problems found at {path}.", err=True)
        raise typer.Exit(1)

    if len(problems) > 1:
        typer.echo(
            f"Multiple problems found in {path}. "
            "Currently, only one problem is supported per file.",
            err=True,
        )
        raise typer.Exit(1)

    problem = problems[0]
    problem.update_config_weak(config)

    return problem


def _handle_invalid_frontend(frontend: str) -> None:
    """Error on an invalid frontend."""
    typer.echo(f"invalid frontend: {frontend}", err=True)
    raise typer.Exit(1)


def _check_problem(problem: Problem[Any, Any]) -> None:
    """Check that problem is valid."""
    try:
        problem.check()
    except AssertionError as err:
        typer.echo(f"{problem.name()} failed some golden tests: {err}", err=True)
        raise typer.Exit(1) from err


# pylint: disable=too-many-arguments
@app.command()
def gen(
    source: str = typer.Argument(
        ...,
        help="The file with the problem to generate.",
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
    inject: List[pathlib.Path] = typer.Option(
        [], "--inject", help="Inject a util file into the submission directory."
    ),
    inject_all: List[pathlib.Path] = typer.Option(
        [],
        "--inject-all",
        help="Inject all util files in the specified folder "
        "into the submission directory.",
    ),
    injection_module: str = typer.Option(
        "injection",
        "--injection-module",
        help="The name of the module to import from the injection directory.",
    ),
    auto_inject: bool = typer.Option(
        False,
        "--auto-inject",
        help="Find the first injection directory recursively and automatically.",
    ),
) -> None:
    """Generate an autograder file for a problem."""
    config = _load_config(config_file)
    _load_injection_config(config, inject, inject_all, injection_module, auto_inject)
    problem = _load_problem(source, config)  # type: ignore
    _check_problem(problem)

    if frontend == "gradescope":
        _gen_gradescope(problem, output)
    else:
        _handle_invalid_frontend(frontend)


# pylint: disable=too-many-arguments
@app.command()
def check(
    source: str = typer.Argument(
        ...,
        help="The problem to check.",
    ),
    config_file: str = typer.Option(
        "aga.toml", "--config", "-c", help="The path to the aga config file."
    ),
    inject: List[pathlib.Path] = typer.Option(
        [], "--inject", help="Inject a util file into the submission directory."
    ),
    inject_all: List[pathlib.Path] = typer.Option(
        [],
        "--inject-all",
        help="Inject all util files in the specified folder "
        "into the submission directory.",
    ),
    injection_module: str = typer.Option(
        "injection",
        "--injection-module",
        help="The name of the module to import from the injection directory.",
    ),
    auto_inject: bool = typer.Option(
        False,
        "--auto-inject",
        help="Find the first injection directory recursively and automatically.",
    ),
) -> None:
    """Check a problem against test cases with an `aga_expect`."""
    config = _load_config(config_file)
    _load_injection_config(config, inject, inject_all, injection_module, auto_inject)
    problem = _load_problem(source, config)  # type: ignore
    _check_problem(problem)
    typer.echo(f"{problem.name()} passed golden tests.")


@app.command()
# pylint: disable=too-many-arguments
def run(
    source: str = typer.Argument(
        ...,
        help="The problem to run.",
    ),
    submission: str = typer.Argument(
        ..., help="The file containing the student submission."
    ),
    config_file: str = typer.Option(
        "aga.toml", "--config", "-c", help="The path to the aga config file."
    ),
    points: float = typer.Option(
        20.0, "--points", help="The total number of points for the problem."
    ),
    due: datetime = typer.Option(
        datetime.now,
        "--due",
        help="The problem due date.",
        show_default="now",  # type: ignore
    ),
    submitted: datetime = typer.Option(
        datetime.now,
        "--submitted",
        help="The problem submission date.",
        show_default="now",  # type: ignore
    ),
    previous_submissions: int = typer.Option(
        0, "--previous_submissions", help="The number of previous submissions."
    ),
    inject: List[pathlib.Path] = typer.Option(
        [], "--inject", help="Inject a util file into the submission directory."
    ),
    inject_all: List[pathlib.Path] = typer.Option(
        [],
        "--inject-all",
        help="Inject all util files in the specified folder "
        "into the submission directory.",
    ),
    injection_module: str = typer.Option(
        "injection",
        "--injection-module",
        help="The name of the module to import from the injection directory.",
    ),
    auto_inject: bool = typer.Option(
        False,
        "--auto-inject",
        help="Find the first injection directory recursively and automatically.",
    ),
) -> None:
    """Run the autograder on an example submission."""
    config = _load_config(config_file)
    _load_injection_config(config, inject, inject_all, injection_module, auto_inject)
    problem: Problem = _load_problem(source, config)  # type: ignore
    metadata = SubmissionMetadata(points, submitted - due, previous_submissions)
    result = load_and_run(problem, submission, metadata)
    print_fancy_summary(result)


click_object = typer.main.get_command(app)  # exposed for documentation
