"""Configuration for `nox`, which runs tests across multiple python versions.

Gradescope's docker autograder container is built on Ubuntu 18.04, which does not
provide a newer python. Therefore, running tests in python3.7 is necessary. Nox does not
handle versioning of your python environment on its own; you can use a tool like `pyenv`
to do so, or just install the python3.7 interpreter from the Python website.

Regardless, nox expects that you have a `python3.7` binary in your $PATH.
"""

import nox
from nox import Session
from nox_poetry import session as nox_session

# default nox sessions (overridden with -s)
nox.options.sessions = ("lint", "test")

python_versions = ("3.9", "3.6")
locations = ["src", "tests"]

test_deps = ("pytest", "pytest-cov", "pytest-lazy-fixture", "pytest-mock", "docker")
linters = (
    "flake8",
    "flake8-black",
    "flake8-bugbear",
    "pydocstyle",
    "mypy",
    "pylint",
)


@nox_session(python=python_versions)
def test(session: Session) -> None:
    """Run pytest in the specified python environment."""
    args = session.posargs or ["--cov"]
    session.install(".")
    session.install(*test_deps)
    session.run("pytest", *args)


@nox.session(python="3.9")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    session.install(".")
    session.install("coverage[toml]", "codecov")
    session.install(*test_deps)
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)


@nox_session(python=python_versions)
def test_slow(session: Session) -> None:
    """Run the slow python tests."""
    args = session.posargs or ["-m slow"]
    session.install(".")
    session.install(*test_deps)
    session.run("pytest", *args)


@nox_session(python=python_versions)
def lint(session: Session) -> None:
    """Run static linters in the specified python environment."""
    args = session.posargs or locations
    session.install(".")
    session.install(*test_deps)  # installed so they type check
    session.install(*linters)
    session.run("flake8", *args)
    session.run("pydocstyle", *args)
    session.run("pylint", *args)
    session.run("mypy", *args)


@nox_session(python="3.9")
def fmt(session: Session) -> None:
    """Format the codebase with black."""
    args = session.posargs or locations
    session.install("black", "isort")
    session.run("black", *args)
    session.run("isort", *args)
