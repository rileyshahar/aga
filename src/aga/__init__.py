"""Aga grades assignments: a library for easily producing autograders for code.

Anything not explicitly documented here should not be used directly by clients and is
only exposed for testing, the CLI, and type hinting.
"""

from importlib.metadata import version

from .core import (
    group,
    problem,
    param,
    test_case,
    test_cases,
    test_cases_params,
    test_cases_product,
    test_cases_zip,
    test_cases_singular_params,
)

__all__ = (
    "problem",
    "param",
    "test_case",
    "test_cases",
    "test_cases_params",
    "test_cases_product",
    "test_cases_zip",
    "test_cases_singular_params",
    "group",
)
__version__ = version(__name__)  # type: ignore
