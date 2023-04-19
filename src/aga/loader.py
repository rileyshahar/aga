"""Tools for loading student-submitted, maybe-invalid code from source files."""

import importlib.util
import os
from glob import glob
from importlib.machinery import ModuleSpec
from os.path import isdir
from os.path import join as pathjoin
from types import ModuleType
from typing import Any, Callable, Iterable, TypeVar

from dill import Unpickler  # type: ignore

from .core import Problem

Output = TypeVar("Output")


class InvalidSubmissionError(BaseException):
    """Something about the submission was invalid."""


class TooManyMatchingSymbols(InvalidSubmissionError):
    """Too many maching symbols were found."""


class NoMatchingSymbol(InvalidSubmissionError, AttributeError):
    """An expected symbol was not found."""


class SubmissionSyntaxError(InvalidSubmissionError, SyntaxError):
    """The submission held an invalid syntax."""

    def __init__(self, file: str):
        super().__init__()
        self.file = file


class NoScript(InvalidSubmissionError, FileNotFoundError):
    """No script was found."""


class MultipleScripts(InvalidSubmissionError):
    """Too many scripts were found."""


def _get_spec_from_path(path: str, name: str) -> ModuleSpec:
    """Get the spec of the module at path."""
    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None:
        # Based on inspection of the source, I'm not certain how this can happen, but my
        # type checker insists it can. This seems like the most reasonable error to
        # raise.
        raise FileNotFoundError

    return spec


def _load_script_from_file(path: str, name: str = "script") -> Callable[[], None]:
    """Load the python script at path as a function."""
    spec = _get_spec_from_path(path, name)
    mod = importlib.util.module_from_spec(spec)

    def inner() -> None:
        # we don't handle errors here so that they'll show up as runtime issues when we
        # run the test
        spec.loader.exec_module(mod)  # type: ignore

    return inner


def _load_script_from_dir(path: str, name: str = "script") -> Callable[[], None]:
    """Load the python script in the directory at path."""
    scripts = glob(pathjoin(path, "*.py"))
    if not scripts:
        raise NoScript
    if len(scripts) > 1:
        raise MultipleScripts

    return _load_script_from_file(scripts[0], name)


def load_script_from_path(path: str, name: str = "script") -> Callable[[], None]:
    """Load the script at path, either a file or directory."""
    if isdir(path):
        return _load_script_from_dir(path, name)
    else:
        return _load_script_from_file(path, name)


def _load_source_from_file(path: str, name: str = "module") -> Any:
    """Load the python source file found at path, absolute or relative, as a module.

    There's a lot of weird stuff going on in this method with type signatures and
    poorly-documented code that python uses internally for their `import` statement. I
    got this implementation from https://stackoverflow.com/a/67692 and made only small
    modifications to it, but I'm not 100% sure I can explain how it works.
    """
    spec = _get_spec_from_path(path, name)
    mod = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(mod)  # type: ignore
    except (SyntaxError, NameError) as err:
        raise SubmissionSyntaxError(path) from err  # group all parse errors
    except ImportError as err:
        raise InvalidSubmissionError(
            "The problem submission file has invalid imports. "
            "Did you forget to use injection options? "
        ) from err

    return mod


def _load_attr_from_module(attr: str, module: ModuleType) -> Any:
    """Get a specific symbol from a module."""
    try:
        return getattr(module, attr)
    except AttributeError as err:
        raise NoMatchingSymbol from err


def _load_from_module_by(
    pred: Callable[[Any], bool], module: ModuleType
) -> Iterable[Any]:
    """Return all items in the module satisfying the predicate."""
    for item in module.__dict__.values():
        if pred(item):
            yield item


def _load_problems_from_module(module: ModuleType) -> Iterable[Problem[Any, Any]]:
    """Return all problems in the module."""
    yield from _load_from_module_by(
        lambda i: isinstance(i, Problem), module  # type: ignore
    )


def load_problems_from_path(path: str) -> Iterable[Problem[Any, Any]]:
    """Load all problems from the module at path."""
    mod = _load_source_from_file(path)
    yield from _load_problems_from_module(mod)


def _load_symbol_from_file(path: str, symbol: str) -> Any:
    """Load a specific symbol from a source file found at path, absolute or relative."""
    mod = _load_source_from_file(path)
    return _load_attr_from_module(symbol, mod)


def _load_symbol_from_dir(path: str, symbol: str) -> Any:
    """Load a specific symbol from any of the source files in a directory."""
    matching_symbols = []
    for file in os.listdir(path):
        try:
            file_path = pathjoin(path, file)
            matching_symbols.append(load_symbol_from_path(file_path, symbol))
        except (FileNotFoundError, NoMatchingSymbol):
            pass

    if len(matching_symbols) > 1:
        raise TooManyMatchingSymbols
    if len(matching_symbols) == 0:
        raise NoMatchingSymbol
    return matching_symbols[0]


def load_symbol_from_path(path: str, symbol: str) -> Any:
    """Load a specific symbol from `path`.

    If path is a directory, load from any file in the directory. If path is a file, load
    from that file.
    """
    if isdir(path):
        return _load_symbol_from_dir(path, symbol)
    else:
        return _load_symbol_from_file(path, symbol)


class _ProblemUnpickler(Unpickler):  # type: ignore
    """A custom unpickler which will always get the `Problem` class from `aga`.

    This is a hack-ish thing which is required because dill expects us to unpickle an
    object in the same module it was pickled in, so it can then find the object's type
    and use that for instantiation. We want to be able to unpickle the object in any
    type, and we know that we always have a Problem pickled at `problem.pckl`, so we can
    just assert that its class should be Problem. This is _highly_ unsafe if we are
    unsure of the safety of `problem.pckl`, but pickle/dill is not remotely safe anyway
    with untrusted data.

    This specific solution will break if dill, for some reason, wants to pickle some
    *other* class named "Problem". In that case, I think the best solution will be to
    look into a custom pickler which changes the module name on that end.
    """

    def find_class(self, module: str, name: str) -> Any:
        if name == "Problem":
            return Problem
        return super().find_class(module, name)


def load_problem(root: str, fname: str = "problem.pckl") -> Problem[Any, Any]:
    """Load a problem from the gradescope environment."""
    with open(pathjoin(root, fname), "rb") as problem_pickled:
        out: Problem[Any, Any] = _ProblemUnpickler(problem_pickled).load()
    return out
